# Documentación del Proyecto: MyDocs.AI

## 1. Introducción

**MyDocs.AI** es una aplicación que permite a los usuarios crear un chatbot personalizado basado en sus propios documentos. El sistema ingiere documentos (texto plano o PDF), los procesa y los indexa para que un modelo de lenguaje (LLM) pueda responder preguntas utilizando únicamente la información contenida en ellos.

El flujo principal se divide en dos partes:
1.  **Entrenamiento**: Cargar un documento y asociarlo a un "bot" mediante un ID único.
2.  **Chat**: Conversar con el bot, que buscará en el documento la información más relevante para responder.

---

## 2. Tecnologías Principales

-   **Backend**: Python
    -   **FastAPI**: Framework web para construir la API REST.
    -   **Uvicorn**: Servidor ASGI para ejecutar la aplicación FastAPI.
-   **Inteligencia Artificial**:
    -   **OpenAI API**: Se utiliza para dos tareas clave:
        1.  **Generación de Embeddings**: Convertir fragmentos de texto en vectores numéricos para su posterior comparación (`text-embedding-ada-002` o similar).
        2.  **Generación de Respuestas**: Utilizar un modelo de lenguaje como GPT-4 o GPT-3.5 para generar respuestas coherentes basadas en un contexto.
    -   **FAISS (Facebook AI Similarity Search)**: Una librería para la búsqueda eficiente de similitud entre vectores. Es el núcleo del sistema de recuperación de información.
-   **Procesamiento de Documentos**:
    -   **PyMuPDF (fitz)**: Librería para extraer texto de archivos PDF.

---

## 3. Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```
mydocs.ai/
├── backend/
│   ├── data/                 # Almacena los fragmentos (chunks) de texto en formato JSON.
│   │   ├── 123_chunks.json
│   │   └── ...
│   ├── faiss_data/           # Almacena los índices vectoriales de FAISS.
│   │   ├── 123.index
│   │   └── ...
│   ├── __init__.py
│   ├── config.py             # Carga la configuración (API keys) desde .env.
│   ├── faiss_index.py        # Lógica para crear y consultar los índices FAISS.
│   ├── main.py               # Archivo principal de FastAPI con los endpoints de la API.
│   ├── openai_client.py      # Cliente para interactuar con la API de OpenAI.
│   └── (context_store.py)    # (Inferido) Módulo para guardar y cargar chunks de texto.
├── frontend/                 # Contiene la interfaz de usuario.
│   ├── index.html            # Página principal del chat.
│   ├── entrenar.html         # Página para subir documentos.
│   └── js/
│       └── ...               # Archivos JavaScript.
├── .env                      # Archivo para variables de entorno (no en el repositorio).
└── requirements.txt          # Dependencias de Python.
```

---

## 4. Cómo Funciona

### 4.1. Configuración Inicial

1.  **Clonar el repositorio.**
2.  **Crear y activar un entorno virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  **Instalar las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Crear el archivo `.env`**: En la raíz del proyecto, crea un archivo llamado `.env` y añade tu clave de API de OpenAI:
    ```
    OPENAI_API_KEY="sk-..."
    ```
5.  **Iniciar el servidor**:
    ```bash
    uvicorn backend.main:app --reload
    ```
    El servidor estará disponible en `http://127.0.0.1:8000`.

### 4.2. Flujo de Entrenamiento (Carga de Documentos)

Este proceso, también llamado "indexación", prepara los documentos para que el bot pueda consultarlos.

1.  **Subida del Documento**: El usuario accede a la página `/entrenar` y sube un archivo (PDF o TXT) junto con un **ID de Usuario** (que actúa como `bot_id`). Esto envía una petición al endpoint `POST /upload-doc`.

2.  **Procesamiento del Texto**:
    -   El backend recibe el archivo y el `user_id`.
    -   Extrae todo el texto del documento. Si es un PDF, usa la librería `fitz`.
    -   El texto completo se divide en fragmentos más pequeños llamados **chunks** (de 500 caracteres cada uno). Esto es crucial para que la búsqueda de similitud sea precisa.

3.  **Generación de Embeddings**:
    -   Cada `chunk` de texto se envía a la API de OpenAI para obtener su **embedding**. Un embedding es un vector de números que representa el significado semántico del texto.

4.  **Creación del Índice FAISS**:
    -   Los embeddings de todos los chunks se utilizan para construir un índice vectorial con FAISS.
    -   Este índice se guarda en el disco como `backend/faiss_data/{user_id}.index`. El índice permite encontrar rápidamente los vectores (y por tanto, los chunks) más similares a un nuevo vector dado.

5.  **Almacenamiento de Chunks**:
    -   Los `chunks` de texto originales se guardan en un archivo JSON en `backend/data/{user_id}_chunks.json` para poder recuperarlos más tarde.

### 4.3. Flujo de Conversación (Chat)

1.  **Envío de Pregunta**: El usuario interactúa con la interfaz de chat (en `/`) y envía un mensaje. La interfaz hace una petición `POST` al endpoint `/chat/{bot_id}`.

2.  **Búsqueda de Chunks Relevantes (Retrieval)**:
    -   El backend recibe el mensaje del usuario y el `bot_id`.
    -   Obtiene el embedding de la pregunta del usuario usando la API de OpenAI.
    -   Utiliza el índice FAISS (`{bot_id}.index`) para buscar los **3 chunks** cuyos embeddings son más similares al embedding de la pregunta.

3.  **Construcción del Contexto**:
    -   Los textos de los 3 chunks más relevantes se concatenan para formar un **contexto**.
    -   Se crea un *prompt* para el modelo de lenguaje de OpenAI que incluye una instrucción clara, el contexto recuperado y la pregunta original del usuario. El prompt se ve algo así:
        ```
        Eres un asistente llamado MyDocs.AI que responde solo con base en este documento. Si no hay información suficiente, decí que no podés ayudar.

        [Texto del chunk 1]
        [Texto del chunk 2]
        [Texto del chunk 3]

        Pregunta del usuario: [Pregunta original]
        ```

4.  **Generación de la Respuesta (Generation)**:
    -   Este prompt se envía a un modelo de chat de OpenAI (ej. GPT-4).
    -   El modelo genera una respuesta basándose **estrictamente** en el contexto proporcionado.

5.  **Respuesta al Usuario**: La respuesta generada por el LLM se devuelve al frontend, que la muestra al usuario.

Este enfoque se conoce como **Retrieval-Augmented Generation (RAG)**.

---

## 5. Endpoints de la API

-   `GET /`
    -   **Descripción**: Sirve la página principal de chat (`index.html`).
-   `GET /entrenar`
    -   **Descripción**: Sirve la página de "entrenamiento" para subir documentos (`entrenar.html`).
-   `POST /upload-doc`
    -   **Descripción**: Sube, procesa e indexa un documento.
    -   **Parámetros (Form-data)**:
        -   `file`: El archivo a subir (`UploadFile`).
        -   `user_id`: El identificador para el bot (`str`).
    -   **Respuesta**: Un JSON con el estado y el número de chunks generados.
-   `POST /chat/{bot_id}`
    -   **Descripción**: Procesa un mensaje de chat y devuelve una respuesta del bot.
    -   **Parámetro (URL)**:
        -   `bot_id`: El ID del bot a consultar (`str`).
    -   **Cuerpo de la Petición (JSON)**:
        -   `message`: La pregunta del usuario (`str`).
    -   **Respuesta**: Un JSON con la respuesta del modelo.
-   `GET /docs/{user_id}`
    -   **Descripción**: Devuelve una lista de los documentos cargados para un `user_id`. **Nota**: La implementación actual de este endpoint y la lógica en `upload-doc` para registrar los nombres de los archivos parecen tener un error y no funcionan como se espera.
-   `POST /ask`
    -   **Descripción**: Una versión simplificada del endpoint de chat.
    -   **Parámetros (Form-data)**:
        -   `user_id`: El ID del bot (`str`).
        -   `question`: La pregunta del usuario (`str`).

---

## 6. Mejoras y Puntos a Considerar

1.  **Gestión de Nombres de Archivo**: La lógica en `POST /upload-doc` para guardar la lista de archivos subidos por usuario es incorrecta. Intenta leer un archivo con el nombre del documento subido (`{user_id}_{filename}`), lee su contenido como una cadena, y luego intenta usar `.append()`, lo que fallará. El endpoint `GET /docs/{user_id}` busca un archivo diferente (`{user_id}_docs.json`). Esta funcionalidad necesita ser corregida para que funcione correctamente.

2.  **Indexación Aditiva**: Actualmente, si se sube un nuevo documento con un `user_id` existente, el índice FAISS y el archivo de chunks se **sobrescriben**. El sistema podría mejorarse para permitir agregar nuevos documentos a un índice existente sin tener que re-procesar los antiguos.

3.  **Manejo de Errores**: Se podría añadir un manejo de errores más detallado, por ejemplo, si la clave de OpenAI no es válida, si un archivo no se puede procesar, o si el `bot_id` no existe durante el chat.

4.  **Persistencia**: El estado (índices y chunks) se guarda en archivos locales. Para un entorno de producción, se podría considerar el uso de un almacenamiento de objetos (como S3) para los archivos y una base de datos de vectores dedicada.