from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# -------------------------
# App setup
# -------------------------
app = FastAPI(title="GlobeAI Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Load embeddings & vector DB
# -------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    "vector_store",
    embeddings,
    allow_dangerous_deserialization=True
)


# -------------------------
# Request model
# -------------------------
class Question(BaseModel):
    question: str


# -------------------------
# Intent detection
# -------------------------
def is_casual_question(question: str) -> bool:
    casual_keywords = [
        "hi", "hello", "hey",
        "how are you",
        "who are you",
        "what can you do",
        "help",
        "thank", "thanks",
        "exam stress",
        "nervous",
        "motivate",
        "how to study",
        "study tips"
    ]
    q = question.lower()
    return any(word in q for word in casual_keywords)


# -------------------------
# Main route
# -------------------------
@app.post("/ask")
def ask(q: Question):
    question = q.question.strip()

    # 1️⃣ CASUAL / GENERAL → AI-GENERATED (SAFE)
    if is_casual_question(question):
        return {
            "answer": (
                "Hello 👋 I am **GlobeAI**.\n\n"
                "I help students with:\n"
                "• BA Political Science syllabus questions\n"
                "• Exam-oriented answers\n"
                "• Study guidance & motivation\n\n"
                "Ask me any subject-related question when you’re ready 📘"
            )
        }

    # 2️⃣ ACADEMIC → RESOURCE-BASED ONLY
    docs = db.similarity_search(question, k=3)

    if not docs:
        return {
            "answer": (
                "❌ This question is not found in the available syllabus resources.\n\n"
                "Please ask a question strictly related to your syllabus."
            )
        }

    # 3️⃣ FORMAT ANSWER (EXAM STYLE)
    answer = "📘 **Answer based on syllabus resources**\n\n"

    answer += "**Introduction:**\n"
    answer += docs[0].page_content[:300] + "\n\n"

    if len(docs) > 1:
        answer += "**Main Points:**\n"
        for d in docs[1:]:
            answer += "- " + d.page_content[:250] + "\n\n"

    answer += "**Conclusion:**\n"
    answer += "The above explanation is based strictly on the prescribed syllabus material."

    return {"answer": answer}


# -------------------------
# Optional home route
# -------------------------
@app.get("/")
def home():
    return {"message": "GlobeAI backend is running"}
