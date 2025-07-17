import os, json, sys, fitz
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, Form
from backend.faiss_index import index_documents, search_similar_chunks
from backend.openai_client import get_openai_response
from backend.supabase_client import supabase


app = FastAPI()
print("✅ sys.path:", sys.path)
print("🔐 Supabase key usada:", os.getenv("SUPABASE_SERVICES_ROLE")[:10])

# Permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas para servir HTML y JS
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="static")

@app.get("/")
def read_login():
    return FileResponse(os.path.join(frontend_dir, "login.html"))


@app.get("/chat")
def read_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/entrenar")
def read_entrenar():
    return FileResponse(os.path.join(frontend_dir, "entrenar.html"))

# 🔥 Endpoint principal del chat
@app.post("/chat/{bot_id}")
async def chat(bot_id: str, request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    user_id = bot_id # Usar el ID del bot de la URL como el ID de usuario

    # Buscar los chunks relevantes del usuario
    chunks = search_similar_chunks(user_id, user_message)
    # Manejar el caso en que el índice no existe para evitar enviar un error a OpenAI
    if chunks and "❌" in chunks[0]:
        return {"response": "Lo siento, no pude encontrar los documentos para este bot. Por favor, asegúrate de que el ID es correcto y que los documentos fueron subidos."}

    context = (
        "Eres un asistente llamado MyDocs.AI que responde solo con base en este documento. "
        "Si no hay información suficiente, decí que no podés ayudar.\n\n"
        + "\n".join(chunks)
    )

    response = get_openai_response(context, user_message)
    return {"response": response}

@app.post("/upload-doc")
async def upload_doc(file: UploadFile, user_id: str = Form(...)):
    content = await file.read()
    filename = file.filename

    print(f"📄 Procesando archivo: {filename}")
    print(f"👤 Usuario: {user_id}")

    # Extraer texto del archivo
    if filename.endswith(".pdf"):
        doc = fitz.open(stream=content, filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
    else:
        text = content.decode("utf-8")

    # Chunkear texto
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    print(f"🧠 Chunks generados: {len(chunks)}")

    # Guardar en FAISS como siempre (si seguís usando eso)
    from backend.faiss_index import index_documents
    index_documents(user_id, chunks)

    # Insertar en Supabase
    try:
        response = supabase.table("documents").insert({
            "user_id": user_id,
            "filename": filename,
            "num_chunks": len(chunks),
            "status": "procesado"
        }).execute()

        print("✅ Documento guardado en Supabase:", response.data)
        return {"status": "ok", "chunks": len(chunks)}
    except Exception as e:
        print("❌ Error al guardar en Supabase:", e)
        return {"status": "error", "message": str(e)}

@app.get("/docs/{user_id}")
def get_user_docs(user_id: str):
    try:
        response = supabase.table("documents").select("*").eq("user_id", user_id).execute()
        print("📄 Documentos encontrados:", response.data)
        return {"docs": response.data}
    except Exception as e:
        print("❌ Error al obtener documentos:", e)
        return {"docs": [], "error": str(e)}


@app.post("/ask")
async def ask_doc(user_id: str = Form(...), question: str = Form(...)):
    chunks = search_similar_chunks(user_id, question)
    context = "\n".join(chunks)
    response = get_openai_response(context, question)
    return {"response": response}
