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

    # --- CONFIGURATION FOR LOCAL OLLAMA ---
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral:latest",
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False
    }

    # FIXED: Perfectly realigned to 4 spaces
    try:
        # INCREASED: timeout changed from 30 to 120 seconds to give your machine breathing room
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            return response.json().get("response", "Error: No text returned from local AI.")
        elif response.status_code == 404:
            return f"AI Generation Error: Model 'mistral:latest' was not found in your local Ollama registry. Run 'ollama pull mistral'."
        else:
            return f"AI Generation Error: Server responded with code {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "System Timeout: The local AI model took longer than 120 seconds to respond. Try closing heavy background apps to free up system memory."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to local Ollama instance. Is Ollama running (`ollama run mistral`)?"
    except Exception as e:
        return f"Error executing direct AI analysis: {str(e)}"