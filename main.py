#!/usr/bin/env python3
"""
Video Generation Agent System
Uses multiple ADK agents to generate videos with AI-powered script, audio, and illustrations
"""

from video_generation_orchestrator import VideoGenerationOrchestrator
import os
from dotenv import load_dotenv

def main():
    """Main entry point for video generation"""
    load_dotenv()
    
    # Get API keys from environment
    gemini_key = os.getenv('GEMINI_API_KEY')
    elevenlabs_key = os.getenv('ELEVEN_LABS_API')
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in .env file")
        return
    
    if not elevenlabs_key:
        print("⚠️  ELEVEN_LABS_API not found - will use gTTS for audio generation")
    
    # Initialize the orchestrator
    orchestrator = VideoGenerationOrchestrator(
        gemini_api_key=gemini_key,
        elevenlabs_api_key=elevenlabs_key
    )
    
    # Example: Generate video about "powerhouse of the cell"
    topic = "powerhouse of the cell"
    print(f"🎬 Generating video about: {topic}")
    
    # Generate the video
    result = orchestrator.generate_video(topic)
    
    if result["success"]:
        print(f"\n🎉 SUCCESS!")
        print(f"📹 Video saved: {result['final_video']}")
        print(f"⏱️  Duration: {result['total_duration']:.1f} seconds")
        print(f"🎭 Scenes: {result['total_scenes']}")
        
        # Save project data
        orchestrator.save_project_data(result, f"{topic}_project_data.json")
    else:
        print(f"\n❌ FAILED: {result['message']}")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 