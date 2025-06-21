#!/usr/bin/env python3
"""
ADK-compatible Video Generation Agent
Integrates the VideoGenerationOrchestrator with Google ADK Development UI
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from dotenv import load_dotenv

# Add the parent directory to the path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_generation_orchestrator import VideoGenerationOrchestrator

load_dotenv()

def generate_video_from_topic(topic: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a complete video from a topic using the VideoGenerationOrchestrator
    
    Args:
        topic (str): The topic for the video
        output_filename (str): Optional custom output filename
        
    Returns:
        dict: Complete result with video generation status and details
    """
    try:
        # Get API keys from environment
        gemini_key = os.getenv('GEMINI_API_KEY')
        elevenlabs_key = os.getenv('ELEVEN_LABS_API')
        
        if not gemini_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY not found in environment variables",
                "message": "Please set your Gemini API key in .env file"
            }
        
        # Initialize the orchestrator
        orchestrator = VideoGenerationOrchestrator(
            gemini_api_key=gemini_key,
            elevenlabs_api_key=elevenlabs_key
        )
        
        # Generate the video
        result = orchestrator.generate_video(topic, output_filename)
        
        if result["success"]:
            # Save project data for reference
            project_file = f"{topic.replace(' ', '_').lower()}_project_data.json"
            orchestrator.save_project_data(result, project_file)
            
            return {
                "success": True,
                "video_path": result["final_video"],
                "duration": result["total_duration"],
                "scenes": result["total_scenes"],
                "project_file": project_file,
                "message": f"Video generated successfully: {result['final_video']}"
            }
        else:
            return result
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate video due to an unexpected error"
        }

def get_project_status() -> Dict[str, Any]:
    """
    Get the status of the video generation system
    
    Returns:
        dict: System status information
    """
    try:
        gemini_key = os.getenv('GEMINI_API_KEY')
        elevenlabs_key = os.getenv('ELEVEN_LABS_API')
        
        status = {
            "gemini_configured": bool(gemini_key),
            "elevenlabs_configured": bool(elevenlabs_key),
            "output_directories": {
                "audio": os.path.exists("static/audio"),
                "videos": os.path.exists("static/videos"),
                "compiled_videos": os.path.exists("static/compiled_videos"),
                "manim_outputs": os.path.exists("static/manim_outputs")
            }
        }
        
        return {
            "success": True,
            "status": status,
            "message": "System status retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get system status"
        }

def list_generated_videos() -> Dict[str, Any]:
    """
    List all generated videos in the output directory
    
    Returns:
        dict: List of generated videos with their details
    """
    try:
        video_dir = "static/compiled_videos"
        if not os.path.exists(video_dir):
            return {
                "success": True,
                "videos": [],
                "message": "No videos directory found"
            }
        
        videos = []
        for filename in os.listdir(video_dir):
            if filename.endswith('.mp4'):
                filepath = os.path.join(video_dir, filename)
                file_stats = os.stat(filepath)
                videos.append({
                    "filename": filename,
                    "path": filepath,
                    "size_bytes": file_stats.st_size,
                    "created": file_stats.st_ctime
                })
        
        return {
            "success": True,
            "videos": videos,
            "count": len(videos),
            "message": f"Found {len(videos)} generated videos"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list generated videos"
        }

# Create the root agent for ADK
root_agent = Agent(
    name="video_generation_agent",
    model="gemini-2.0-flash",
    description="AI-powered video generation agent that creates complete videos with script, audio, and illustrations",
    instruction="""
    You are a sophisticated video generation agent that can create complete videos from topics.
    
    Your capabilities include:
    1. Generate complete videos from any topic using generate_video_from_topic()
    2. Check system status and configuration using get_project_status()
    3. List previously generated videos using list_generated_videos()
    
    When generating videos, you will:
    - Create an engaging script broken into scenes
    - Generate audio narration for each scene
    - Find or create appropriate illustrations (Getty Images or mathematical visualizations)
    - Compile everything into a final video with intro/outro
    
    Always provide helpful information about the video generation process and any issues encountered.
    """,
    tools=[
        generate_video_from_topic,
        get_project_status,
        list_generated_videos
    ]
) 