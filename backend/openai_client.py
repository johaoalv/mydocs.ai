from openai import OpenAI
import os
from backend.config import OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_openai_response(context, user_message):
    try:
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_message}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al conectar con OpenAI: {str(e)}"
    

def get_embeddings(text_list: list[str]):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text_list
    )
    return [r.embedding for r in response.data]
