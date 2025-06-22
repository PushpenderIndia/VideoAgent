from google.adk.agents import LlmAgent
from agents.video_script_agent import VideoScriptAgent
from agents.audio_generation_agent import AudioGenerationAgent
from agents.video_illustration_agent import VideoIllustrationAgent
from agents.manim_illustration_agent import ManimIllustrationAgent
from agents.video_compiler_agent import VideoCompilerAgent
import os
import json
from dotenv import load_dotenv

load_dotenv()

class VideoGenerationOrchestrator:
    def __init__(self, gemini_api_key=None, elevenlabs_api_key=None):
        """
        Initialize all agents for video generation
        """
        self.script_agent = VideoScriptAgent(gemini_api_key)
        self.audio_agent = AudioGenerationAgent(elevenlabs_api_key)
        self.illustration_agent = VideoIllustrationAgent(gemini_api_key)
        self.manim_agent = ManimIllustrationAgent(gemini_api_key)
        self.compiler_agent = VideoCompilerAgent()
        
        # Create necessary directories
        os.makedirs("static/audio", exist_ok=True)
        os.makedirs("static/videos", exist_ok=True)
        os.makedirs("static/compiled_videos", exist_ok=True)
    
    def generate_video(self, topic: str, output_filename: str = None) -> dict:
        """
        Complete video generation workflow
        
        Args:
            topic (str): Topic for the video
            output_filename (str): Custom output filename
            
        Returns:
            dict: Complete result with final video path
        """
        if not output_filename:
            output_filename = f"{topic.replace(' ', '_').lower()}_video.mp4"
        
        print(f"🎬 Starting video generation for topic: {topic}")
        
        # Step 1: Generate Script
        print("📝 Generating video script...")
        script_result = self.script_agent.generate_script(topic)
        
        if not script_result["success"]:
            return {
                "success": False,
                "error": script_result["error"],
                "step": "script_generation",
                "message": "Failed to generate script"
            }
        
        script_data = script_result["script"]
        scenes = script_data["scenes"]
        
        print(f"✅ Script generated with {len(scenes)} scenes")
        
        # Step 2: Process each scene
        processed_scenes = []
        
        for i, scene in enumerate(scenes):
            print(f"🎭 Processing scene {i+1}/{len(scenes)}: {scene['title']}")
            
            scene_result = self._process_scene(scene, i)
            
            if scene_result["success"]:
                processed_scenes.append(scene_result["scene_data"])
                print(f"✅ Scene {i+1} processed successfully")
            else:
                print(f"❌ Scene {i+1} failed: {scene_result['error']}")
                return {
                    "success": False,
                    "error": scene_result["error"],
                    "step": f"scene_{i}_processing",
                    "message": f"Failed to process scene {i+1}"
                }
        
        # Step 3: Compile Final Video
        print("🎥 Compiling final video...")
        compilation_result = self.compiler_agent.compile_final_video(
            processed_scenes, 
            output_filename,
            video_illustration_agent=self.illustration_agent
        )
        
        if not compilation_result["success"]:
            return {
                "success": False,
                "error": compilation_result["error"],
                "step": "video_compilation",
                "message": "Failed to compile final video"
            }
        
        # Step 4: Add intro/outro
        print("🎬 Adding intro and outro...")
        enhanced_result = self.compiler_agent.add_intro_outro(
            compilation_result["final_video"],
            intro_text=f"Video: {topic.title()}",
            outro_text="Thank you for watching!"
        )
        
        final_video_path = enhanced_result.get("enhanced_video", compilation_result["final_video"])
        
        print(f"🎉 Video generation completed!")
        print(f"📹 Final video: {final_video_path}")
        
        return {
            "success": True,
            "final_video": final_video_path,
            "topic": topic,
            "total_scenes": len(scenes),
            "total_duration": compilation_result["total_duration"],
            "script_data": script_data,
            "processed_scenes": processed_scenes,
            "message": f"Video generated successfully: {final_video_path}"
        }
    
    def _process_scene(self, scene: dict, scene_index: int) -> dict:
        """
        Process a single scene: generate audio and find/create illustrations
        
        Args:
            scene (dict): Scene data with title and content
            scene_index (int): Index of the scene
            
        Returns:
            dict: Processed scene data
        """
        try:
            # Combine all content lines into dialogue
            dialogue = " ".join(scene["content"])
            
            # Generate audio for the dialogue
            print(f"🔊 Generating audio for scene {scene_index + 1}...")
            audio_result = self.audio_agent.generate_audio_from_text(dialogue)
            
            if not audio_result["success"]:
                return {
                    "success": False,
                    "error": audio_result["error"],
                    "scene_index": scene_index
                }
            
            # Check if scene needs mathematical illustration
            print(f"🧮 Checking for mathematical content...")
            manim_result = self.manim_agent.create_illustration_for_dialogue(dialogue)
            
            scene_data = {
                "title": scene["title"],
                "content": scene["content"],
                "dialogue": dialogue,
                "audio_file": audio_result["audio_file"],
                "scene_index": scene_index
            }
            
            if manim_result["success"] and manim_result["needs_illustration"]:
                # Use Manim-generated illustration
                print(f"🎨 Using Manim illustration for mathematical content")
                scene_data["manim_video"] = manim_result["video_file"]
                scene_data["illustration_type"] = "manim"
                scene_data["content_type"] = manim_result["content_type"]
            else:
                # Find unique video illustration from Getty Images using title and dialogue
                print(f"🔍 Finding unique video illustration with title priority...")
                scene_title = scene["title"]
                illustration_result = self.illustration_agent.find_illustration_for_dialogue(dialogue, scene_index, scene_title)
                
                if illustration_result["success"]:
                    scene_data["video_url"] = illustration_result["video_url"]
                    scene_data["poster_url"] = illustration_result["poster_url"]
                    scene_data["keyword_used"] = illustration_result.get("keyword_used", "")
                    scene_data["illustration_type"] = "getty_video"
                    print(f"✅ Found unique video for scene {scene_index + 1} using title: '{scene_title}' with keyword: '{scene_data['keyword_used']}'")
                else:
                    # No unique illustration found, will use text overlay
                    scene_data["illustration_type"] = "text_overlay"
                    print(f"⚠️  No unique video found for scene {scene_index + 1} with title: '{scene_title}', using text overlay")
            
            return {
                "success": True,
                "scene_data": scene_data,
                "scene_index": scene_index
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "scene_index": scene_index
            }
    
    def save_project_data(self, result: dict, output_path: str = "project_data.json"):
        """
        Save complete project data for future reference
        
        Args:
            result (dict): Complete video generation result
            output_path (str): Path to save project data
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"💾 Project data saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Failed to save project data: {e}")


# Example usage and CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate videos using AI agents")
    parser.add_argument("topic", help="Topic for the video")
    parser.add_argument("--output", "-o", help="Output filename", default=None)
    parser.add_argument("--save-project", "-s", help="Save project data", action="store_true")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = VideoGenerationOrchestrator(
        gemini_api_key=os.getenv('GEMINI_API_KEY'),
        elevenlabs_api_key=os.getenv('ELEVEN_LABS_API')
    )
    
    # Generate video
    result = orchestrator.generate_video(args.topic, args.output)
    
    if result["success"]:
        print(f"\n🎉 SUCCESS!")
        print(f"📹 Video: {result['final_video']}")
        print(f"⏱️  Duration: {result['total_duration']:.1f} seconds")
        print(f"🎭 Scenes: {result['total_scenes']}")
        
        if args.save_project:
            orchestrator.save_project_data(result)
    else:
        print(f"\n❌ FAILED: {result['message']}")
        print(f"Error: {result.get('error', 'Unknown error')}") 