import os, json, sys, fitz
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, Form
from backend.faiss_index import index_documents, search_similar_chunks
from backend.openai_client import get_openai_response

app = FastAPI()
print("✅ sys.path:", sys.path)
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

    # ⬇️ Guarda nombre de documento en un JSON específico del usuario
    filename = file.filename
    path = os.path.join("backend/data", f"{user_id}_docs.json")
    docs_list = []
    if os.path.exists(path):
        with open(path, "r") as f:
            docs_list = json.load(f)
    
    if filename not in docs_list:
        docs_list.append(filename)
    
    with open(path, "w") as f:
        json.dump(docs_list, f)

    if file.filename.endswith(".pdf"):
       
        doc = fitz.open(stream=content, filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
    else:
        text = content.decode("utf-8")

    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    index_documents(user_id, chunks)
    return {"status": "ok", "chunks": len(chunks)}

#endpoint para ver docs cargados
@app.get("/docs/{user_id}")
def get_user_docs(user_id: str):
    path = os.path.join("backend/data", f"{user_id}_docs.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return {"docs": json.load(f)}
    return {"docs": []}


@app.post("/ask")
async def ask_doc(user_id: str = Form(...), question: str = Form(...)):
    chunks = search_similar_chunks(user_id, question)
    context = "\n".join(chunks)
    response = get_openai_response(context, question)
    return {"response": response}
