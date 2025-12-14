import os
import uuid
import time
import json
import logging
import textwrap
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

# DynamoDB persistence modules
from app.user_store import get_or_create_user, charge_credits, get_user_credits
from app.session_store import (
    load_state, save_state, append_turn,
    update_retrieval_context, update_preferences
)
from app.message_store import log_message

# Load .env file
load_dotenv()

# Load API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPTCustomPromptPlanner:
    def __init__(self, vector_path="vector", model_name="gpt-4-turbo", temperature=0.4, default_session_id=None):
        """
        Initialize GPT Custom Prompt Planner with DynamoDB persistence.
        
        Args:
            vector_path: Path to FAISS vector store
            model_name: OpenAI model name
            temperature: LLM temperature
            default_session_id: Default session ID (from env or 'default')
        """
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in environment.")
        self.vector_path = vector_path
        self.model_name = model_name
        self.temperature = temperature
        self.default_session_id = default_session_id or os.getenv("DEFAULT_SESSION_ID", "default")
        self._load_vectorstore()
        self._load_model()

    def _load_vectorstore(self):
        embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.load_local(
            self.vector_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

    def _load_model(self):
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

    def enrich_prompt(self, user_prompt, age, gender, height_cm, present_weight, target_weight, calories, conversation_history=None):
        goal = "gain" if target_weight and present_weight and target_weight > present_weight else "lose"
        
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
        
        # Add conversation history if available (group into turns)
        if conversation_history and len(conversation_history) > 0:
            prompt += "\n**Conversation History:**\n"

            # Group messages into conversation turns (pairs of user + assistant)
            history_pairs = []
            last_6_messages = conversation_history[-6:]  # Last 3 exchanges (6 messages)

            for i in range(0, len(last_6_messages), 2):
                if i + 1 < len(last_6_messages):
                    user_msg = last_6_messages[i]
                    asst_msg = last_6_messages[i + 1]

                    if user_msg.get("role") == "user" and asst_msg.get("role") == "assistant":
                        history_pairs.append((user_msg.get("text", ""), asst_msg.get("text", "")))
                elif i < len(last_6_messages):
                    # Handle odd number of messages (last user message without response)
                    user_msg = last_6_messages[i]
                    if user_msg.get("role") == "user":
                        history_pairs.append((user_msg.get("text", ""), None))

            # Format as conversation turns
            for turn_num, (user_text, asst_text) in enumerate(history_pairs, 1):
                prompt += f"\n**Turn {turn_num}:**\n"
                prompt += f"- User: {user_text}\n"
                if asst_text:
                    prompt += f"- Assistant: {asst_text}\n"

            prompt += "\n"
        
        prompt += f"""
**Current User Question:**
{user_prompt}

**Instructions for GPT:**
1. Your response must be based on user details and retrieved context.
2. Consider the conversation history above when answering.
3. Consider topics like weight management, food suggestions, calorie balance, physical activity, dietary nutrients, macronutrients (carbs, protein, fat), and micronutrients (e.g., vitamins, minerals).
4. Make it short and better by representing facts clearly.
5. If the question is clearly unrelated to health, weight, exercise, or nutrition, respond with:
   *"This question appears unrelated to personalized health guidance. Please ask about nutrition, exercise, or weight-related planning."*
"""
        return prompt.strip()

    def generate(
        self,
        user_prompt,
        user_id="test-user-1",
        session_id=None,
        age=None,
        gender=None,
        height_cm=None,
        present_weight=None,
        target_weight=None,
        calories=None,
        score_threshold=0.5,
        credit_cost=1
    ):
        """
        Generate RAG response with full DynamoDB persistence.
        
        Args:
            user_prompt: User's question
            user_id: User identifier (default: "test-user-1", later: Cognito sub)
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
            
            # Extract preference values with defaults
            age_val = merged_prefs.get("age")
            gender_val = merged_prefs.get("gender")
            height_val = merged_prefs.get("height_cm")
            present_wt = merged_prefs.get("present_weight")
            target_wt = merged_prefs.get("target_weight")
            cal_val = merged_prefs.get("calories")
            
            # Step 5: Run FAISS retrieval (original logic preserved)
            docs_and_scores = self.vectorstore.similarity_search_with_score(user_prompt, k=7)
            
            valid_sources = {"diet", "physical", "Weight", "GymDataset", "weight_gain", "weight_loss", "Human_Nut", "Nut_Science"}
            
            # Filter by score and valid source
            filtered = [
                (doc, score) for doc, score in docs_and_scores
                if doc.metadata.get("source") in valid_sources and score <= score_threshold
            ]
            
            docs = [doc for doc, _ in filtered]
            cosine_scores = [score for _, score in filtered]
            
            print("📄 Filtered Sources (score ≤ threshold):")
            for doc, score in zip(docs, cosine_scores):
                print(f" - {doc.metadata.get('source')}, Score: {score:.4f}")
            
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
            
            # Build document summaries for return (original logic)
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
            
            # Step 6: Build enriched prompt with conversation history (original logic)
            conversation_history = state.get("recent_turns", [])
            prompt = self.enrich_prompt(
                user_prompt, 
                age_val, 
                gender_val, 
                height_val, 
                present_wt, 
                target_wt, 
                cal_val,
                conversation_history=conversation_history  # Pass conversation history
            )
            
            # Combine context and prompt
            context = "\n\n".join([doc.page_content for doc in docs])
            full_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"
            
            # Step 7: Call GPT with retrieved context (original logic)
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
