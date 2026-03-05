import fitz  # PyMuPDF
import faiss
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import ollama # Import the new Ollama library
import json # You'll need this to parse the JSON response from Ollama
# ----------------------------
# Configuration
# ----------------------------
file_paths = {
    "Brooklyn": "pdfs/Brooklyn_Indictments/8_29_24_9Trey.pdf"
}
load_dotenv()
embedding_model_name = "BAAI/bge-small-en-v1.5"
llm_model_name = "gemma:2b"


# ----------------------------
# Load embedding model
# ----------------------------
model = SentenceTransformer(embedding_model_name)


# ----------------------------
# Utilities
# ----------------------------
def extract_text(path: str) -> str:
    """Extract text from a PDF file."""
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks of words."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i: i + chunk_size]
        chunks.append(" ".join(chunk))  # ensure chunks are strings
        i += chunk_size - overlap
    return chunks


def build_index(chunks: list[str], batch_size: int = 32):
    """Embed chunks in batches, save to disk, and return FAISS index + chunks + embeddings."""
    embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = model.encode(chunks[i:i+batch_size])
        embeddings.extend(batch)

    embeddings = np.array(embeddings)

    # Save to disk
    np.save("embeddings.npy", embeddings)
    with open("chunks.json", "w") as f:
        json.dump(chunks, f)

    # Build FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, chunks, embeddings

def load_index():
    """Load FAISS index + chunks from disk."""
    embeddings = np.load("embeddings.npy")
    with open("chunks.json", "r") as f:
        chunks = json.load(f)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, chunks, embeddings

def retrieve(query: str, chunks: list[str], index, k: int = 3) -> list[str]:
    """Retrieve top-k chunks relevant to the query."""
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, k)
    results = [chunks[i] for i in I[0] if i < len(chunks)]

    print("Retrieved passages:\n", results)

    return [chunks[i] for i in I[0] if i < len(chunks)]


def query_llm(query: str, context_chunks: list[str]) -> str:
    """Send query + context to OpenAI and return the answer."""
    context = "\n".join(context_chunks)
    prompt = f"""
        You are an AI assistant analyzing RICO indictment press releases.
        Answer the question using ONLY the provided context below.
        If the answer is not explicitly in the context, say "Not found in context."
        Question: {query}
        Context: {context}
        Answer:
    """
    try:
        response = ollama.chat(
            model=llm_model_name,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ]
        )
        return response['message']['content']
    except ollama.ResponseError as e:
        print(f"Error from Ollama: {e.error}")
        return "An error occurred while communicating with the local LLM."




# ----------------------------
# Main Pipeline
# ----------------------------
def run_pipeline(query: str):
    # Try loading existing index
    if os.path.exists("embeddings.npy") and os.path.exists("chunks.json"):
        print("Loading existing index...")
        index, chunks, embeddings = load_index()
    else:
        print("Building new index...")
        all_chunks = []
        for label, path in file_paths.items():
            print(f"Processing {label}...")
            text = extract_text(path)
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
        index, chunks, embeddings = build_index(all_chunks)

    # Retrieve context
    retrieved_passages = retrieve(query, chunks, index, k=3)

    # Query LLM
    answer = query_llm(query, retrieved_passages)

    return answer


if __name__ == "__main__":
    query = "Can you describe the people charged in this indictment? Please list the people and their legal charges"
    result = run_pipeline(query)
    print("Answer:\n", result)
