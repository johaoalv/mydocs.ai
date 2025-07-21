import os
import faiss
import numpy as np
from backend.openai_client import get_embeddings
from backend.context_store import save_context, load_context


INDEX_DIR = "backend/faiss_data"
os.makedirs(INDEX_DIR, exist_ok=True)

def index_documents(user_id: str, chunks: list[str]):
    print(f"📦 Indexando documento de {user_id} con {len(chunks)} chunks")

    for i, ch in enumerate(chunks):
        print(f"🧩 Chunk {i}: {ch[:120].replace('\n', ' ')}...")
    embeddings = get_embeddings(chunks)
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    faiss.write_index(index, os.path.join(INDEX_DIR, f"{user_id}.index"))
    save_context(user_id, chunks)

def search_similar_chunks(user_id: str, question: str, top_k=3) -> list[str]:
    index_path = os.path.join(INDEX_DIR, f"{user_id}.index")
    if not os.path.exists(index_path):
        print("❌ No se encontró índice FAISS para este usuario.")
        return ["❌ No se encontró un índice para este usuario"]

    index = faiss.read_index(index_path)
    chunks = load_context(user_id)

    print(f"\n🔍 Buscando chunks similares para: \"{question}\"")
    print(f"🧠 Chunks cargados: {len(chunks)}")

    q_embedding = get_embeddings([question])[0]
    D, I = index.search(np.array([q_embedding]).astype("float32"), top_k)

    print("📎 Chunks más relevantes encontrados:")
    for i in I[0]:
        if i < len(chunks):
            print(f" → Chunk {i}: {chunks[i][:120].replace('\n', ' ')}...")

    return [chunks[i] for i in I[0] if i < len(chunks)]