#config.py
import os
from dotenv import load_dotenv

load_dotenv() 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Falta la OPENAI_API_KEY en el archivo .env")

#puedes servir las envs en cualquier archivo de esta manera

# from dotenv import load_dotenv
# load_dotenv()


