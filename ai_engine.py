import requests
import json
import re
from config import get_config
from knowledge_manager import get_system_prompt_extension, update_knowledge_from_ai

# Load configuration
config = get_config()

def run_direct_astrology_analysis(house_context_string):
    # ... (Keep your prompt setup code as is)
    memory_extension = get_system_prompt_extension()
    base_system_prompt = "You are an expert Jyotish Master..."
    full_system_prompt = f"{base_system_prompt}\n\n{memory_extension}"
    user_prompt = f"Please provide a deep interpretation based on this structural data:\n\n{house_context_string}"

    url = f"{config.OLLAMA_URL}/api/generate"
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": f"{full_system_prompt}\n\n{user_prompt}",
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=config.OLLAMA_TIMEOUT)
        
        if response.status_code == 200:
            full_text = response.json().get("response", "Error: No text returned.")
            
            # Extract and Strip 'NEEDED_LEARNING'
            # This regex looks for 'NEEDED_LEARNING:' and everything after it
            pattern = r"NEEDED_LEARNING:(.*)"
            match = re.search(pattern, full_text, re.DOTALL)
            
            cleaned_analysis = full_text
            if match:
                # Save the findings to your knowledge manager
                update_knowledge_from_ai(match.group(0))
                # Remove the section from the text that goes to the UI
                cleaned_analysis = re.sub(pattern, "", full_text, flags=re.DOTALL).strip()
            
            return cleaned_analysis
        
        elif response.status_code == 404:
            return f"AI Generation Error: Model '{config.OLLAMA_MODEL}' not found."
        else:
            return f"AI Generation Error: Code {response.status_code}"
            
    except Exception as e:
        return f"Error executing direct AI analysis: {str(e)}"