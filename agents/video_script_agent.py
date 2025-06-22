from google.adk.agents import LlmAgent
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

class VideoScriptAgent(LlmAgent):
    def __init__(self, gemini_api_key=None):
        super().__init__(
            name="VideoScriptAgent",
            description="Generates 2-minute video scripts in a structured JSON format"
        )
        self._initialize_config(gemini_api_key)
    
    def _initialize_config(self, gemini_api_key):
        """Initialize configuration after parent initialization"""
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.__dict__['model'] = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_script(self, topic: str) -> dict:
        """
        Generate a 2-minute video script for the given topic
        
        Args:
            topic (str): The topic for the video script
            
        Returns:
            dict: Script in JSON format with scenes and content
        """
        prompt = f'''Write a 2 min video script of this topic in an interactive way: "{topic}"

I want this in a json format with strictly these keys:
{{"scenes": [{{"title": "", "content": ["line1", "line2"]}}, {{"title": "", "content": ["line1", "line2"]}},{{"title": "", "content": ["line1", "line2"]}},]}}

Make sure:
- The script is engaging and interactive
- Each scene has a clear title
- Content is broken down into digestible lines
- Total duration should be around 2 minutes when spoken
- Include 5-7 scenes for good pacing
- Do not include extra instructions or comments in the script, just the dialogue
'''
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000
                )
            )
            
            script_text = response.text
            
            # Extract JSON from the response
            start_idx = script_text.find('{')
            end_idx = script_text.rfind('}') + 1
            json_str = script_text[start_idx:end_idx]
            
            script_data = json.loads(json_str)
            
            return {
                "success": True,
                "script": script_data,
                "message": f"Generated script for topic: {topic}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate script"
            } 