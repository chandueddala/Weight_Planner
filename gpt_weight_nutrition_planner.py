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

class GPTWeightNutritionPlanner:
    def __init__(self, vector_path="vector", model_name="gpt-4-turbo", temperature=0.3):
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in environment.")
        self.vector_path = vector_path
        self.model_name = model_name
        self.temperature = temperature
        self._load_vectorstore()
        self._load_model()

    def _load_vectorstore(self):
        embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.load_local(self.vector_path, embeddings, allow_dangerous_deserialization=True)

    def _load_model(self):
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        self.chain = load_qa_with_sources_chain(self.llm, chain_type="stuff")

    def build_prompt(self, age, gender, height_cm, present_weight, target_weight, activity, calories):
        goal = "gain" if target_weight > present_weight else "lose"
        return f"""
The user wants to {goal} weight.

**User Details:**
- Age: {age}
- Gender: {gender}
- Height: {height_cm} cm
- Current Weight: {present_weight} kg
- Target Weight: {target_weight} kg
- Activity Level: {activity}
- Suggested Caloric Intake: {calories} kcal/day

**Instructions:**
1. Provide a beginner-friendly weekly physical activity/exercise clearly must be week's day by day.
2. Suggest dietary and nutritional guidance using the context clearly.
"""

    def generate(self, age, gender, height_cm, present_weight, target_weight, activity, calories):
        # Focused query for retrieval
        retrieval_query = f"Weekly or dayly physical activity exercises  and nutrition guidance for someone trying to {'gain' if target_weight > present_weight else 'lose'} weight."
        # Retrieve relevant documents
        docs = self.vectorstore.similarity_search(retrieval_query, k=7)
        valid_sources = [ "diet", "physical", "Weight", "GymDataset", "weight_gain", "weight_loss","Human_Nut","Nut_Science"]
        docs = [doc for doc in docs if doc.metadata.get("source") in valid_sources]
        print("📄 Retrieved Sources:")
        for doc in docs:
            print(" -", doc.metadata.get("source"))

        # Build readable summaries
        doc_summaries = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown Source")
            snippet = doc.page_content[:600].strip().replace("\n", " ") + "..."
            doc_summaries.append(f"**Chunk {i+1} — Source:** {source}\n{textwrap.fill(snippet, width=100)}")

        # Build personalized prompt
        prompt = self.build_prompt(age, gender, height_cm, present_weight, target_weight, activity, calories)

        # Call GPT with retrieved context and full prompt
        response = self.chain.run({"input_documents": docs, "question": prompt})

        return prompt.strip(), response.strip(), doc_summaries
