import os
import json

BASE_PATH = "backend/data"

def save_context(user_id: str, chunks: list[str]):
    os.makedirs(BASE_PATH, exist_ok=True)
    path = os.path.join(BASE_PATH, f"{user_id}_chunks.json")
    with open(path, "w") as f:
        json.dump(chunks, f)

def load_context(user_id: str) -> list[str]:
    path = os.path.join(BASE_PATH, f"{user_id}_chunks.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []
