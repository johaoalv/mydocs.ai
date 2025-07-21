import json
from backend.supabase_client import supabase

BUCKET = "my-docs-ai"

def save_context(doc_id: str, chunks: list[str]):
    # Serializa los chunks y súbelos como json
    data = json.dumps(chunks).encode('utf-8')
    filename = f"{doc_id}_chunks.json"
    supabase.storage.from_(BUCKET).upload(filename, data, {"content-type": "application/json"})

def load_context(doc_id: str) -> list[str]:
    filename = f"{doc_id}_chunks.json"
    try:
        res = supabase.storage.from_(BUCKET).download(filename)
        return json.loads(res) # download() ahora devuelve bytes directamente
    except Exception as e:
        print("❌ Error leyendo chunks de storage:", e)
        return []
