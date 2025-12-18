import os
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_PATH = "../data/BA_Political_Science"
VECTOR_PATH = "vector_store"
MAX_PAGES = 25


def extract_text(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages[:MAX_PAGES]:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text


def main():
    texts = []

    for root, _, files in os.walk(DATA_PATH):
        for file in files:
            if file.lower().endswith(".pdf"):
                print(f"Reading: {file}")
                content = extract_text(os.path.join(root, file))
                if len(content) > 500:
                    texts.append(content)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    docs = splitter.create_documents(texts)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(VECTOR_PATH)

    print("✅ DEMO knowledge base created")


if __name__ == "__main__":
    main()
