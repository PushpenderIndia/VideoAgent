from google.adk.agents import LlmAgent
import google.generativeai as genai
import os
import subprocess
import json
from dotenv import load_dotenv
from manim import *

load_dotenv()

class ManimIllustrationAgent(LlmAgent):
    def __init__(self, gemini_api_key=None):
        super().__init__(
            name="ManimIllustrationAgent",
            description="Generates mathematical and graphical illustrations using Manim"
        )
        self._initialize_config(gemini_api_key)
    
    def _initialize_config(self, gemini_api_key):
        """Initialize configuration after parent initialization"""
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.__dict__['model'] = genai.GenerativeModel('gemini-2.0-flash')
        self.__dict__['output_dir'] = "static/manim_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def detect_mathematical_content(self, dialogue: str) -> dict:
        """
        Detect if dialogue contains mathematical content that needs Manim illustration
        
        Args:
            dialogue (str): The dialogue to analyze
            
        Returns:
            dict: Analysis result with mathematical content detection
        """
        prompt = f'''Analyze this dialogue and determine if it contains mathematical content that would benefit from visual illustration (graphs, equations, geometric shapes, data visualization, etc.):

"{dialogue}"

Respond with JSON in this exact format:
{{"needs_manim": true/false, "content_type": "equation/graph/geometry/data/none", "description": "brief description of what should be illustrated"}}'''
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            
            analysis_text = response.text
            
            # Extract JSON from the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            json_str = analysis_text[start_idx:end_idx]
            
            analysis_data = json.loads(json_str)
            
            return {
                "success": True,
                "needs_manim": analysis_data["needs_manim"],
                "content_type": analysis_data["content_type"],
                "description": analysis_data["description"],
                "dialogue": dialogue,
                "message": "Mathematical content analysis completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "needs_manim": False,
                "dialogue": dialogue,
                "message": "Failed to analyze mathematical content"
            }
    
    def generate_manim_code(self, dialogue: str, content_type: str, description: str) -> dict:
        """
        Generate Manim code for creating mathematical illustrations
        
        Args:
            dialogue (str): The dialogue content
            content_type (str): Type of mathematical content
            description (str): Description of what to illustrate
            
        Returns:
            dict: Generated Manim code
        """
        prompt = f'''Generate Manim code to create a visual illustration for this content:

Dialogue: "{dialogue}"
Content Type: {content_type}
Description: {description}

Requirements:
1. Create a class that inherits from Scene
2. Use appropriate Manim objects and animations
3. Keep it simple and clear for a 2-minute video
4. Include proper timing for animations
5. Make it visually appealing

Return only the Python code without any explanations.'''
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=2000
                )
            )
            
            manim_code = response.text
            
            # Clean up the code (remove markdown formatting if present)
            if "```python" in manim_code:
                manim_code = manim_code.split("```python")[1].split("```")[0].strip()
            elif "```" in manim_code:
                manim_code = manim_code.split("```")[1].split("```")[0].strip()
            
            return {
                "success": True,
                "manim_code": manim_code,
                "dialogue": dialogue,
                "content_type": content_type,
                "message": "Manim code generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "dialogue": dialogue,
                "message": "Failed to generate Manim code"
            }
    
    def create_manim_video(self, manim_code: str, scene_name: str, output_name: str = None) -> dict:
        """
        Execute Manim code to create video illustration
        
        Args:
            manim_code (str): The Manim Python code
            scene_name (str): Name of the scene class in the code
            output_name (str): Custom output filename
            
        Returns:
            dict: Result with video file path
        """
        if not output_name:
            output_name = f"manim_scene_{scene_name.lower()}"
        
        # Create a temporary Python file with the Manim code
        temp_file = os.path.join(self.output_dir, f"{output_name}.py")
        
        try:
            with open(temp_file, 'w') as f:
                f.write("from manim import *\n\n")
                f.write(manim_code)
            
            # Run Manim to generate the video
            cmd = [
                "manim",
                temp_file,
                scene_name,
                "--media_dir", self.output_dir,
                "--quality", "medium_quality",
                "--format", "mp4"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find the generated video file
                video_file = os.path.join(self.output_dir, "videos", f"{output_name}", "720p30", f"{scene_name}.mp4")
                
                if os.path.exists(video_file):
                    return {
                        "success": True,
                        "video_file": video_file,
                        "scene_name": scene_name,
                        "message": "Manim video created successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Video file not found after rendering",
                        "message": "Manim execution completed but video not found"
                    }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Manim execution failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create Manim video"
            }
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def create_illustration_for_dialogue(self, dialogue: str) -> dict:
        """
        Complete workflow: analyze dialogue and create Manim illustration if needed
        
        Args:
            dialogue (str): The dialogue to create illustration for
            
        Returns:
            dict: Complete result with video file if mathematical content detected
        """
        # Detect mathematical content
        analysis = self.detect_mathematical_content(dialogue)
        
        if not analysis["success"] or not analysis["needs_manim"]:
            return {
                "success": False,
                "needs_illustration": False,
                "dialogue": dialogue,
                "message": "No mathematical content detected or analysis failed"
            }
        
        # Generate Manim code
        code_result = self.generate_manim_code(
            dialogue, 
            analysis["content_type"], 
            analysis["description"]
        )
        
        if not code_result["success"]:
            return code_result
        
        # Create the video
        import re
        # Extract class name from code
        class_match = re.search(r'class\s+(\w+)\s*\(Scene\)', code_result["manim_code"])
        if not class_match:
            return {
                "success": False,
                "error": "Could not find Scene class in generated code",
                "message": "Invalid Manim code structure"
            }
        
        scene_name = class_match.group(1)
        video_result = self.create_manim_video(
            code_result["manim_code"], 
            scene_name,
            f"illustration_{hash(dialogue[:50]) % 10000}"
        )
        
        return {
            "success": video_result["success"],
            "needs_illustration": True,
            "dialogue": dialogue,
            "video_file": video_result.get("video_file"),
            "content_type": analysis["content_type"],
            "description": analysis["description"],
            "message": video_result["message"]
        } 