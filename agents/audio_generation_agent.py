from google.adk.agents import LlmAgent
import requests
import os
from dotenv import load_dotenv
from gtts import gTTS
import random
import string

load_dotenv()

class AudioGenerationAgent(LlmAgent):
    def __init__(self, elevenlabs_api_key=None, character="Daniel"):
        super().__init__(
            name="AudioGenerationAgent",
            description="Generates audio from text using ElevenLabs API with fallback to gTTS"
        )
        
        # Initialize configuration after super().__init__
        self._initialize_config(elevenlabs_api_key, character)
    
    def _initialize_config(self, elevenlabs_api_key, character):
        """Initialize configuration after parent initialization"""
        character_dict = {
            "Daniel": "onwK4e9ZLuTAKqWW03F9",
            "Female": "21m00Tcm4TlvDq8ikWAM"
        }
        
        # Store API configuration
        api_key = elevenlabs_api_key or os.getenv('ELEVEN_LABS_API')
        self.__dict__['url'] = f"https://api.elevenlabs.io/v1/text-to-speech/{character_dict[character]}"
        self.__dict__['headers'] = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
    
    def _generate_random_chars(self, length=4):
        """Generate random string for unique filenames"""
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    
    def generate_audio_from_text(self, text: str, output_dir: str = "static/audio") -> dict:
        """
        Generate audio file from text using ElevenLabs API with gTTS fallback
        
        Args:
            text (str): Text to convert to speech
            output_dir (str): Directory to save audio files
            
        Returns:
            dict: Result with audio file path and generation method
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        random_suffix = self._generate_random_chars()
        output_file = os.path.join(output_dir, f"audio_{random_suffix}.mp3")
        
        try:
            # Try ElevenLabs first
            model_id = "eleven_multilingual_v2"
            voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
            
            data = {
                "text": text,
                "model_id": model_id,
                "voice_settings": voice_settings
            }
            
            response = requests.post(self.url, json=data, headers=self.headers)
            response.raise_for_status()
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            
            return {
                "success": True,
                "audio_file": output_file,
                "method": "ElevenLabs",
                "text": text,
                "message": f"Audio generated successfully using ElevenLabs"
            }
            
        except Exception as e:
            # Fallback to gTTS
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(output_file)
                
                return {
                    "success": True,
                    "audio_file": output_file,
                    "method": "gTTS",
                    "text": text,
                    "message": f"Audio generated successfully using gTTS (ElevenLabs failed: {str(e)})"
                }
                
            except Exception as gtts_error:
                return {
                    "success": False,
                    "error": f"Both ElevenLabs and gTTS failed. ElevenLabs: {str(e)}, gTTS: {str(gtts_error)}",
                    "text": text,
                    "message": "Failed to generate audio"
                }
    
    def generate_audio_batch(self, text_list: list, output_dir: str = "static/audio") -> dict:
        """
        Generate audio files for a list of texts
        
        Args:
            text_list (list): List of texts to convert to speech
            output_dir (str): Directory to save audio files
            
        Returns:
            dict: Results with all generated audio files
        """
        results = []
        successful = 0
        failed = 0
        
        for i, text in enumerate(text_list):
            result = self.generate_audio_from_text(text, output_dir)
            results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        return {
            "success": failed == 0,
            "results": results,
            "summary": {
                "total": len(text_list),
                "successful": successful,
                "failed": failed
            },
            "message": f"Generated {successful}/{len(text_list)} audio files successfully"
        } 