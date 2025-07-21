import faiss
import numpy as np
from backend.supabase_client import supabase
from backend.context_store_sp import save_context, load_context
from backend.openai_client import get_embeddings

BUCKET = "my-docs-ai"

def index_documents(doc_id: str, chunks: list[str]):
    print(f"📦 Indexando documento {doc_id} con {len(chunks)} chunks")
    embeddings = get_embeddings(chunks)
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    # Serializa y sube el FAISS index a Supabase Storage
    # Guarda el index en memoria temporal (bytes buffer)
    faiss_index_array = faiss.serialize_index(index)
    supabase.storage.from_(BUCKET).upload(
        f"{doc_id}.index", # Usamos el ID del documento
        faiss_index_array.tobytes(),  # Convertir el ndarray a bytes
        {"content-type": "application/octet-stream", "x-upsert": "true"}
    )
    # Guarda los chunks como JSON en Storage
    save_context(doc_id, chunks)

def search_similar_chunks(user_id: str, question: str, top_k=3) -> list[str]:
    # 1. Encontrar todos los documentos para el usuario
    try:
        response = supabase.table("documents").select("id").eq("user_id", user_id).eq("status", "procesado").execute()
        doc_ids = [doc['id'] for doc in response.data]
        if not doc_ids:
            return ["❌ No se encontraron documentos procesados para este usuario."]
    except Exception as e:
        print(f"❌ Error obteniendo documentos para el usuario {user_id}: {e}")
        return ["❌ Error al buscar documentos."]

    print(f"\n🔍 Buscando chunks similares para: \"{question}\"")
    q_embedding = get_embeddings([question])[0]
    
    all_results = []

    # 2. Iterar sobre cada documento, buscar y recolectar resultados
    for doc_id in doc_ids:
        try:
            # Bajar el índice y los chunks para este documento
            res_bytes = supabase.storage.from_(BUCKET).download(f"{doc_id}.index")
            index_data = np.frombuffer(res_bytes, dtype='uint8')
            index = faiss.deserialize_index(index_data)
            chunks = load_context(doc_id)

            # Buscar en este índice
            D, I = index.search(np.array([q_embedding]).astype("float32"), top_k)
            
            # Guardar los resultados con su distancia y contenido
            for i, dist in zip(I[0], D[0]):
                if i < len(chunks):
                    all_results.append({'distance': dist, 'chunk': chunks[i]})

        except Exception as e:
            print(f"⚠️ No se pudo buscar en el documento {doc_id}: {e}")
            continue

    # 3. Ordenar todos los resultados de todos los documentos por distancia y devolver los mejores
    all_results.sort(key=lambda x: x['distance'])
    
    top_chunks = [result['chunk'] for result in all_results[:top_k]]

    print(f"📎 {len(top_chunks)} chunks más relevantes encontrados en total.")
    return top_chunks