#!/usr/bin/env python3
"""
Demo script showing individual agent usage
"""

import os
from dotenv import load_dotenv
from agents.video_script_agent import VideoScriptAgent
from agents.audio_generation_agent import AudioGenerationAgent
from agents.video_illustration_agent import VideoIllustrationAgent
from agents.manim_illustration_agent import ManimIllustrationAgent
from agents.video_compiler_agent import VideoCompilerAgent

load_dotenv()

def demo_script_agent():
    """Demo the video script generation agent"""
    print("🎬 Demo: Video Script Agent")
    print("-" * 30)
    
    agent = VideoScriptAgent()
    topic = "photosynthesis"
    
    print(f"Generating script for topic: {topic}")
    result = agent.generate_script(topic)
    
    if result["success"]:
        print("✅ Script generated successfully!")
        print(f"Number of scenes: {len(result['script']['scenes'])}")
        
        # Show first scene
        first_scene = result['script']['scenes'][0]
        print(f"First scene title: {first_scene['title']}")
        print(f"First scene content: {first_scene['content'][:2]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    return result

def demo_audio_agent():
    """Demo the audio generation agent"""
    print("\n🔊 Demo: Audio Generation Agent")
    print("-" * 30)
    
    agent = AudioGenerationAgent()
    text = "Photosynthesis is the process by which plants convert sunlight into energy."
    
    print(f"Generating audio for: {text[:50]}...")
    result = agent.generate_audio_from_text(text)
    
    if result["success"]:
        print(f"✅ Audio generated using {result['method']}")
        print(f"Audio file: {result['audio_file']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    return result

def demo_illustration_agent():
    """Demo the video illustration agent"""
    print("\n🔍 Demo: Video Illustration Agent")
    print("-" * 30)
    
    agent = VideoIllustrationAgent()
    dialogue = "Plants absorb sunlight through their green leaves using chlorophyll."
    
    print(f"Finding illustrations for: {dialogue[:50]}...")
    result = agent.find_illustration_for_dialogue(dialogue)
    
    if result["success"]:
        print("✅ Illustration found!")
        print(f"Keywords: {result['keywords']}")
        if result['best_video']:
            print(f"Best video URL: {result['best_video']['video_url'][:50]}...")
    else:
        print(f"❌ Failed: {result.get('error', 'No videos found')}")
    
    return result

def demo_manim_agent():
    """Demo the Manim illustration agent"""
    print("\n🧮 Demo: Manim Illustration Agent")
    print("-" * 30)
    
    agent = ManimIllustrationAgent()
    dialogue = "The equation for photosynthesis is 6CO2 + 6H2O + light energy → C6H12O6 + 6O2"
    
    print(f"Analyzing mathematical content: {dialogue[:50]}...")
    result = agent.create_illustration_for_dialogue(dialogue)
    
    if result["success"] and result["needs_illustration"]:
        print("✅ Mathematical content detected!")
        print(f"Content type: {result['content_type']}")
        print(f"Description: {result['description']}")
        if result.get("video_file"):
            print(f"Manim video: {result['video_file']}")
    else:
        print("ℹ️  No mathematical content detected or generation failed")
    
    return result

def demo_compiler_agent():
    """Demo the video compiler agent"""
    print("\n🎥 Demo: Video Compiler Agent")
    print("-" * 30)
    
    agent = VideoCompilerAgent()
    
    # Create dummy scene data
    scene_data = {
        "title": "Introduction to Photosynthesis",
        "content": ["Plants need sunlight", "They convert light to energy"],
        "audio_file": "static/audio/demo_audio.mp3",  # Would need real file
        "illustration_type": "text_overlay"
    }
    
    print("Creating scene video...")
    # Note: This would need a real audio file to work
    print("ℹ️  Skipping actual compilation (needs real audio file)")
    print("✅ Video compiler agent ready")
    
    return {"success": True, "message": "Demo completed"}

def main():
    """Run all agent demos"""
    print("🎬 Video Generation Agent System Demo")
    print("=" * 40)
    
    # Check API keys
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment")
        print("Please set up your .env file with API keys")
        return
    
    # Run demos
    demos = [
        demo_script_agent,
        demo_audio_agent,
        demo_illustration_agent,
        demo_manim_agent,
        demo_compiler_agent
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    print("\n🎉 Demo completed!")
    print("To generate a full video, run: python main.py")

if __name__ == "__main__":
    main() 