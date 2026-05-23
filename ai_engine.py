import os
import requests
import json

def run_direct_astrology_analysis(house_context_string):
    """
    Sends the compiled database and calculation context directly to a local 
    Ollama instance (or an external API) without the overhead of CrewAI agents.
    """
    # System instructions to keep the model grounded in real data
    system_prompt = (
        "You are an expert Vedic Astrologer (Jyotish Master). Your task is to interpret "
        "the provided astrological house context. Use the structural rules, planetary positions, "
        "and dignity flags provided in the context. Be precise, clear, and objective. "
        "Do not invent data outside the provided parameters."
    )
    
    # User payload combining everything we gathered
    user_prompt = f"Please provide a deep interpretation based on this structural data:\n\n{house_context_string}"

    # --- CONFIGURATION FOR LOCAL OLLAMA (e.g., Llama 3 or Mistral) ---
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",  # Replace with whichever model you have downloaded locally
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "Error: No text returned from local AI.")
        else:
            return f"AI Generation Error: Server responded with code {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to local Ollama instance. Is Ollama running (`ollama run llama3`)?"
    except Exception as e:
        return f"Error executing direct AI analysis: {str(e)}"