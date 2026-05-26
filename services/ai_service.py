# AI and LLM integration service
import requests
import logging
from config import get_config
from knowledge_manager import get_system_prompt_extension, update_knowledge_from_ai

logger = logging.getLogger(__name__)
config = get_config()


class AIAnalysisService:
    """Service for AI-powered astrological analysis"""
    
    def __init__(self):
        self.ollama_url = config.OLLAMA_URL
        self.model = config.OLLAMA_MODEL
        self.timeout = config.OLLAMA_TIMEOUT
    
    def analyze_chart(self, house_context_string):
        """
        Analyze a chart using local LLM (Ollama).
        
        Args:
            house_context_string: Formatted chart data for analysis
            
        Returns:
            str: AI-generated interpretation or error message
        """
        if not config.ENABLE_AI_ANALYSIS:
            return "AI analysis is disabled in configuration"
        
        try:
            # Build the prompt
            memory_extension = get_system_prompt_extension()
            base_prompt = self._get_base_prompt()
            full_prompt = f"{base_prompt}\n\n{memory_extension}"
            user_message = f"Please provide a deep interpretation based on this structural data:\n\n{house_context_string}"
            
            # Make request to Ollama
            response = self._call_ollama(full_prompt, user_message)
            
            if not response:
                return "Failed to get response from AI model"
            
            # Process response
            return self._process_response(response)
            
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama server")
            return f"AI unavailable: Cannot connect to {self.ollama_url}"
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return f"AI analysis error: {str(e)}"
    
    def _call_ollama(self, system_prompt, user_prompt):
        """Make HTTP request to Ollama API"""
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json().get("response")
            elif response.status_code == 404:
                logger.error(f"Model '{self.model}' not found in Ollama")
                return None
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timeout after {self.timeout}s")
            return None
    
    def _get_base_prompt(self):
        """Get the base system prompt for Jyotish analysis"""
        return """You are an expert Jyotish Master with deep knowledge of Vedic astrology.
        
Your role is to:
1. Analyze planetary placements and their combinations
2. Explain house influences and significances
3. Provide practical life guidance based on the chart
4. Reference classical Jyotish principles
5. Consider yogas (planetary combinations) and their effects

Guidelines:
- Base interpretation strictly on the provided planetary data
- Explain the 'why' behind each planetary influence
- Use clear, structured formatting
- Balance technical accuracy with practical wisdom
- Highlight favorable and challenging periods/areas"""
    
    def _process_response(self, full_text):
        """Process AI response and extract learning insights"""
        try:
            # Extract and store learning insights if present
            if "NEEDED_LEARNING:" in full_text:
                import re
                pattern = r"NEEDED_LEARNING:(.*)"
                match = re.search(pattern, full_text, re.DOTALL)
                if match and config.ENABLE_KNOWLEDGE_UPDATE:
                    update_knowledge_from_ai(match.group(0))
                
                # Remove the learning section from output
                cleaned = re.sub(pattern, "", full_text, flags=re.DOTALL).strip()
                return cleaned
            
            return full_text
        except Exception as e:
            logger.warning(f"Response processing error: {e}")
            return full_text
    
    def is_available(self):
        """Check if Ollama service is available"""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self):
        """Get list of available models from Ollama"""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to get models list: {e}")
            return []
