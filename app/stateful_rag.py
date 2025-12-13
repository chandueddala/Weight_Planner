"""
Production-Ready Stateful RAG Service with DynamoDB Persistence
Integrates LangChain RAG with DynamoDB for user sessions, credit management, and audit logging.
"""
import os
import uuid
import time
import json
import logging
import textwrap
from typing import Tuple, List, Dict, Any
from datetime import datetime, timezone

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

from app.user_store import get_or_create_user, charge_credits, get_user_credits
from app.session_store import (
    load_state, save_state, append_turn,
    update_retrieval_context, update_preferences, build_context_prompt
)
from app.message_store import log_message

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure OpenAI API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


class StatefulRAGPlanner:
    """
    Production RAG service with:
    - User authentication and credit management
    - Stateful conversation sessions
    - Query/response audit logging
    - Idempotent operations for reliability
    """
    
    def __init__(
        self,
        vector_path: str = "vector",
        model_name: str = None,
        temperature: float = 0.4,
        default_session_id: str = None
    ):
        """
        Initialize the stateful RAG planner.
        
        Args:
            vector_path: Path to FAISS vector store
            model_name: OpenAI model name (default from env: MODEL_NAME or 'gpt-4-turbo')
            temperature: LLM temperature parameter
            default_session_id: Default session ID (from env: DEFAULT_SESSION_ID or 'default')
        """
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in environment.")
        
        self.vector_path = vector_path
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4-turbo")
        self.temperature = temperature
        self.default_session_id = default_session_id or os.getenv("DEFAULT_SESSION_ID", "default")
        
        self._load_vectorstore()
        self._load_model()
    
    def _load_vectorstore(self):
        """Load FAISS vector store with embeddings."""
        embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.load_local(
            self.vector_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"Loaded vector store from {self.vector_path}")
    
    def _load_model(self):
        """Load ChatOpenAI LLM."""
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        logger.info(f"Loaded model: {self.model_name}")
    
    def _build_prompt(
        self,
        user_prompt: str,
        preferences: Dict[str, Any],
        session_context: str = ""
    ) -> str:
        """
        Build enriched prompt with user preferences and session context.
        
        Args:
            user_prompt: User's question
            preferences: User preferences dict (age, gender, weight goals, etc.)
            session_context: Optional conversation context from session
        
        Returns:
            Enriched prompt string
        """
        age = preferences.get("age", "N/A")
        gender = preferences.get("gender", "N/A")
        height_cm = preferences.get("height_cm", "N/A")
        present_weight = preferences.get("present_weight", "N/A")
        target_weight = preferences.get("target_weight", "N/A")
        calories = preferences.get("calories", "N/A")
        
        # Determine goal
        goal = "maintain"
        if target_weight != "N/A" and present_weight != "N/A":
            try:
                goal = "gain" if float(target_weight) > float(present_weight) else "lose"
            except (ValueError, TypeError):
                pass
        
        prompt = f"""
User wants to {goal} weight. Answer the following question using the provided context and tailor the response to the user's personal metrics if possible.

**User Details:**
- Age: {age}
- Gender: {gender}
- Height: {height_cm} cm
- Current Weight: {present_weight} kg
- Target Weight: {target_weight} kg
- Caloric Target: {calories} kcal/day
"""
        
        # Add session context if available
        if session_context:
            prompt += f"\n**Session Context:**\n{session_context}\n"
        
        prompt += f"""
**User Question:**
{user_prompt}

**Instructions for GPT:**
1. Your response must be based on user details and retrieved context.
2. Consider topics like weight management, food suggestions, calorie balance, physical activity, dietary nutrients, macronutrients (carbs, protein, fat), and micronutrients (e.g., vitamins, minerals).
3. Make it short and better by representing facts clearly.
4. If the question is clearly unrelated to health, weight, exercise, or nutrition, respond with:
   *"This question appears unrelated to personalized health guidance. Please ask about nutrition, exercise, or weight-related planning."*
"""
        return prompt.strip()
    
    def generate(
        self,
        user_prompt: str,
        user_id: str = "test-user-1",
        session_id: str = None,
        age: Any = None,
        gender: str = None,
        height_cm: Any = None,
        present_weight: Any = None,
        target_weight: Any = None,
        calories: Any = None,
        score_threshold: float = 0.5,
        credit_cost: int = 1
    ) -> Tuple[str, str, List[str], Dict[str, Any]]:
        """
        Generate RAG response with full DynamoDB integration.
        
        Args:
            user_prompt: User's question
            user_id: User identifier (will be Cognito sub in production)
            session_id: Session identifier (uses default if None)
            age, gender, height_cm, present_weight, target_weight, calories: User preferences
            score_threshold: FAISS similarity threshold (lower = more similar)
            credit_cost: Number of credits to charge for this request
        
        Returns:
            Tuple of (prompt, response, doc_summaries, metadata)
            metadata includes: request_id, credits_remaining, latency_ms, etc.
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        session_id = session_id or self.default_session_id
        start_time = time.time()
        
        logger.info(json.dumps({
            "action": "generate_start",
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id
        }))
        
        try:
            # Step 1: Get or create user
            user = get_or_create_user(user_id)
            initial_credits = user.get("credits_remaining", 0)
            
            # Step 2: Charge credits BEFORE calling LLM (fail fast)
            try:
                charge_credits(user_id, cost=credit_cost, request_id=request_id)
            except ValueError as e:
                logger.warning(json.dumps({
                    "action": "insufficient_credits",
                    "request_id": request_id,
                    "user_id": user_id,
                    "credits": initial_credits
                }))
                return (
                    "",
                    f"Insufficient credits. You have {initial_credits} credits remaining.",
                    [],
                    {"request_id": request_id, "error": "insufficient_credits"}
                )
            
            # Step 3: Load session state
            state = load_state(user_id, session_id)
            
            # Step 4: Update preferences if provided
            preferences = {
                "age": age,
                "gender": gender,
                "height_cm": height_cm,
                "present_weight": present_weight,
                "target_weight": target_weight,
                "calories": calories
            }
            # Filter out None values
            preferences = {k: v for k, v in preferences.items() if v is not None}
            if preferences:
                state = update_preferences(state, preferences)
            
            # Use stored preferences from session if not provided
            stored_prefs = state.get("preferences", {})
            merged_prefs = {**stored_prefs, **preferences}
            
            # Step 5: Build condensed retrieval query with context
            session_context = build_context_prompt(state)
            enriched_query = user_prompt
            if session_context:
                enriched_query = f"{session_context} | {user_prompt}"
            
            # Step 6: Run FAISS retrieval
            docs_and_scores = self.vectorstore.similarity_search_with_score(
                enriched_query, k=7
            )
            
            valid_sources = {
                "diet", "physical", "Weight", "GymDataset",
                "weight_gain", "weight_loss", "Human_Nut", "Nut_Science"
            }
            
            # Filter by score and valid source
            filtered = [
                (doc, score) for doc, score in docs_and_scores
                if doc.metadata.get("source") in valid_sources and score <= score_threshold
            ]
            
            docs = [doc for doc, _ in filtered]
            cosine_scores = [score for _, score in filtered]
            
            logger.info(json.dumps({
                "action": "retrieval_complete",
                "request_id": request_id,
                "retrieved_chunks": len(docs)
            }))
            
            # Build retrieval metadata for logging
            retrieval_meta = [
                {
                    "source": doc.metadata.get("source", "unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", f"chunk_{i}"),
                    "score": float(score)
                }
                for i, (doc, score) in enumerate(zip(docs, cosine_scores))
            ]
            
            # Update session with retrieval context
            state = update_retrieval_context(state, retrieval_meta)
            
            # Build document summaries for return
            doc_summaries = []
            for i, (doc, score) in enumerate(zip(docs, cosine_scores)):
                source = doc.metadata.get("source", "Unknown Source")
                snippet = doc.page_content[:600].strip().replace("\n", " ") + "..."
                doc_summaries.append(
                    f"**Chunk {i+1} — Source: {source}, Similarity Score: {score:.4f}**\n{textwrap.fill(snippet, width=100)}"
                )
            
            if not docs:
                response_text = "No relevant chunks found. Sorry, no context matched your question well enough."
                
                # Log user message and assistant response
                log_message(
                    user_id=user_id,
                    session_id=session_id,
                    role="user",
                    text=user_prompt,
                    request_id=request_id
                )
                log_message(
                    user_id=user_id,
                    session_id=session_id,
                    role="assistant",
                    text=response_text,
                    request_id=request_id,
                    model=self.model_name
                )
                
                # Update session state
                state = append_turn(state, user_prompt, response_text)
                save_state(user_id, session_id, state)
                
                return ("", response_text, [], {"request_id": request_id})
            
            # Step 7: Build full prompt and call LLM
            prompt = self._build_prompt(user_prompt, merged_prefs, session_context)
            context = "\n\n".join([doc.page_content for doc in docs])
            full_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"
            
            response = self.llm.invoke(full_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Step 8: Log user message
            log_message(
                user_id=user_id,
                session_id=session_id,
                role="user",
                text=user_prompt,
                request_id=request_id,
                retrieval_meta=retrieval_meta
            )
            
            # Step 9: Log assistant response
            log_message(
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                text=response_text,
                request_id=request_id,
                model=self.model_name,
                latency_ms=latency_ms
            )
            
            # Step 10: Update session state
            state = append_turn(state, user_prompt, response_text)
            save_state(user_id, session_id, state)
            
            # Get remaining credits
            remaining_credits = get_user_credits(user_id)
            
            metadata = {
                "request_id": request_id,
                "credits_remaining": remaining_credits,
                "latency_ms": latency_ms,
                "chunks_retrieved": len(docs),
                "session_id": session_id
            }
            
            logger.info(json.dumps({
                "action": "generate_complete",
                "request_id": request_id,
                "user_id": user_id,
                "latency_ms": latency_ms,
                "credits_remaining": remaining_credits
            }))
            
            return prompt.strip(), response_text.strip(), doc_summaries, metadata
            
        except Exception as e:
            logger.error(json.dumps({
                "action": "generate_error",
                "request_id": request_id,
                "user_id": user_id,
                "error": str(e)
            }))
            raise
