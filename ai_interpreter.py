import sqlite3
import ollama
from db import fetch_house_tree

def generate_ai_interpretation(snapshot_id: int, house_num: int) -> str:
    data_tree = fetch_house_tree(snapshot_id, house_num)
    
    system_prompt = (
        "You are an expert Vedic Astrologer (Jyotish Master). Analyze the provided data tree. "
        "Explain how the combinations and active planetary influences shape the user's life.\n\n"
        "Rules:\n"
        "1. Base your interpretation strictly on the active nodes listed.\n"
        "2. Explain why a planet is impacting this house using its lineage and rationale.\n"
        "3. Keep your response insightful, clear, and structured with clean formatting."
    )
    
    user_message = f"Structural data tree:\n\n{data_tree}"
    
    try:
        response = ollama.chat(
            model='mistral',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Could not connect to local Ollama engine: {e}. Ensure 'ollama run mistral' is running."