from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

def setup_rag():
    # 1. Load the text
    with open("finance_info.txt") as f:
        finance_text = f.read()

    # 2. Split it into small chunks
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=0)
    docs = text_splitter.create_documents([finance_text])

    # 3. Create the "Vector Search" engine (FAISS)
    # This turns words into numbers so the AI can search them
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # 4. Save it locally
    vectorstore.save_local("faiss_index")
    print("✅ RAG Library Created!")

if __name__ == "__main__":
    setup_rag()

