
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import numpy as np
import subprocess

# ------------------------
# Extract text from PDF
# ------------------------
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

# ------------------------
# Split text into chunks for embedding
# ------------------------
def split_text_into_chunks(text, chunk_size=800, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

# ------------------------
# Embed chunks using a sentence-transformer model
# ------------------------
def embed_text_chunks(chunks, model_name="all-MiniLM-L6-v2"):
    embedder = SentenceTransformer(model_name)
    embeddings = embedder.encode(chunks)
    return embeddings, embedder

# ------------------------
# Create FAISS index for fast similarity search
# ------------------------
def create_faiss_index(embeddings):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index

# ------------------------
# Retrieve top-k relevant chunks based on question
# ------------------------
def retrieve_top_chunks(query, index, embedder, texts, k=5):
    q_vec = embedder.encode([query])
    _, indices = index.search(np.array(q_vec), k)
    return "\n".join([texts[i] for i in indices[0]])

# ------------------------
# Use local LLM via Ollama to answer question
# ------------------------
def ask_question_with_context(context, query, model="llama3.2:latest"):
    prompt = f"""You are a helpful assistant. Read the following text and answer the user's question clearly and concisely.

Context:
{context}

Question:
{query}
Answer:"""
    result = subprocess.run(["ollama", "run", model], input=prompt.encode(), capture_output=True)
    return result.stdout.decode()

# ------------------------
# Full RAG pipeline
# ------------------------
def run_rag_pipeline(pdf_path, question, index=None, embedder=None, chunks=None):
    if index is None or embedder is None or chunks is None:
        # First-time setup
        raw_text = extract_text_from_pdf(pdf_path)
        print(f"📄 Extracted {len(raw_text)} characters from the PDF.")
        chunks = split_text_into_chunks(raw_text)
        print(f"🔢 Split into {len(chunks)} chunks.")
        embeddings, embedder = embed_text_chunks(chunks)
        index = create_faiss_index(np.array(embeddings))
    context = retrieve_top_chunks(question, index, embedder, chunks)
    answer = ask_question_with_context(context, question)
    return answer, index, embedder, chunks


