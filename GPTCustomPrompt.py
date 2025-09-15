import os
import textwrap
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Load API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class GPTCustomPromptPlanner:
    def __init__(self, vector_path="vector", model_name="gpt-4-turbo", temperature=0.4):
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in environment.")
        self.vector_path = vector_path
        self.model_name = model_name
        self.temperature = temperature
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
        self.chain = load_qa_with_sources_chain(self.llm, chain_type="stuff")

    def enrich_prompt(self, user_prompt, age, gender, height_cm, present_weight, target_weight, calories):
        goal = "gain" if target_weight > present_weight else "lose"
        return f"""
User wants to {goal} weight. Answer the following question using the provided context and tailor the response to the user's personal metrics if possible.

**User Details:**
- Age: {age}
- Gender: {gender}
- Height: {height_cm} cm
- Current Weight: {present_weight} kg
- Target Weight: {target_weight} kg
- Caloric Target: {calories} kcal/day

**User Question:**
{user_prompt}

**Instructions for GPT:**
1. Your response must be based only be as per the user deatils and on the retrieved .
2. Consider topics like weight management, food suggestions,calorie balance, ,physical activity, dietary nutrients, macronutrients (carbs, protein, fat), and micronutrients (e.g., vitamins, minerals).
4. Make it Short and better by representing it .
3. If the question is clearly unrelated to health, weight, exercise, or nutrition, respond with:
   *"This question appears unrelated to personalized health guidance. Please ask about nutrition, exercise, or weight-related planning."*
"""

    def generate(self, user_prompt, age, gender, height_cm, present_weight, target_weight, calories, score_threshold=0.5):
        docs_and_scores = self.vectorstore.similarity_search_with_score(user_prompt, k=7)

        valid_sources = { "diet", "physical", "Weight", "GymDataset", "weight_gain", "weight_loss","Human_Nut","Nut_Science"}

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

        doc_summaries = []
        for i, (doc, score) in enumerate(zip(docs, cosine_scores)):
            source = doc.metadata.get("source", "Unknown Source")
            snippet = doc.page_content[:600].strip().replace("\n", " ") + "..."
            doc_summaries.append(
                f"**Chunk {i+1} — Source: {source}, Similarity Score: {score:.4f}**\n{textwrap.fill(snippet, width=100)}"
            )

        if not docs:
            return "No relevant chunks found.", "Sorry, no context matched your question well enough.", []

        prompt = self.enrich_prompt(user_prompt, age, gender, height_cm, present_weight, target_weight, calories)
        response = self.chain.run({"input_documents": docs, "question": prompt})

        return prompt.strip(), response.strip(), doc_summaries
