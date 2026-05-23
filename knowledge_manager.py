import json
import os

KNOWLEDGE_FILE = 'ai_knowledge_base.json'

def load_knowledge():
    if not os.path.exists(KNOWLEDGE_FILE):
        # Initialize the baseline knowledge if file doesn't exist
        initial_data = {
            "known_concepts": ["rashi_fundamentals", "house_rulership"],
            "current_depth": 1,
            "mastery_summary": "Understands basics of 12 Houses and Rashi lords.",
            "next_learning_targets": ["planetary_dignity", "aspect_drishti"]
        }
        save_knowledge(initial_data)
        return initial_data
    with open(KNOWLEDGE_FILE, 'r') as f:
        return json.load(f)

def save_knowledge(data):
    with open(KNOWLEDGE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def update_knowledge_from_ai(ai_raw_response):
    """
    Parses the AI response for a 'NEEDED_LEARNING' section and updates the JSON state.
    """
    knowledge = load_knowledge()
    
    # Simple check if AI reported new learning needs
    if "NEEDED_LEARNING" in ai_raw_response:
        # In a real production scenario, we'd use regex to extract the specific text
        # For now, this marks the trigger that the AI is asking for more depth
        knowledge["last_audit_flag"] = "AI_REQUESTED_UPGRADE"
        save_knowledge(knowledge)
        return True
    return False

def get_system_prompt_extension():
    """
    Generates the string to append to your prompts so the AI 'remembers' its state.
    """
    k = load_knowledge()
    return (
        f"--- CONTINUOUS LEARNING STATE ---\n"
        f"Current Depth: Level {k['current_depth']}\n"
        f"Concepts Mastered: {', '.join(k['known_concepts'])}\n"
        f"Goal: {k['mastery_summary']}\n"
        "If you encounter complex data that goes beyond these concepts, clearly "
        "identify it in a section marked 'NEEDED_LEARNING'."
    )