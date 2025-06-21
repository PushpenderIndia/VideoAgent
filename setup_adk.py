#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for integrating Google ADK with VideoAgent project
"""

import os
import sys
import shutil
from pathlib import Path

def create_adk_structure():
    """Create the necessary directory structure for ADK integration"""
    
    # Create ADK agents directory
    adk_dir = Path("adk_agents")
    adk_dir.mkdir(exist_ok=True)
    
    # Create .env template if it doesn't exist
    env_file = adk_dir / ".env"
    if not env_file.exists():
        env_content = """# Google AI Configuration (Choose one approach)
# Option 1: Using Google AI Studio (Recommended for development)
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_ai_studio_api_key_here

# Option 2: Using Google Cloud Vertex AI (Uncomment if using Vertex AI)
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_CLOUD_PROJECT=your_project_id
# GOOGLE_CLOUD_LOCATION=us-central1

# Video Generation API Keys
GEMINI_API_KEY=your_google_ai_studio_api_key_here
ELEVEN_LABS_API=your_elevenlabs_api_key_here
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print(f"Created .env template at {env_file}")
        print("Please update the API keys in the .env file")
    
    print(f"ADK directory structure created at {adk_dir}")

def install_dependencies():
    """Install required dependencies"""
    print("Installing/updating dependencies...")
    
    # Check if google-adk is already installed
    try:
        import google.adk
        print("google-adk is already installed")
    except ImportError:
        print("Installing google-adk...")
        os.system("pip3 install google-adk")
    
    # Check other dependencies
    dependencies = [
        "google-generativeai",
        "requests", 
        "moviepy",
        "python-dotenv",
        "manim",
        "gtts",
        "easygoogletranslate",
        "cloudscraper"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"{dep} is available")
        except ImportError:
            print(f"Installing {dep}...")
            os.system(f"pip3 install {dep}")

def create_run_script():
    """Create convenient run scripts for ADK"""
    
    # Create run_adk_web.py
    run_web_content = """#!/usr/bin/env python3
'''
Run ADK Web UI for VideoAgent
'''

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to adk_agents directory
    adk_dir = Path("adk_agents")
    if not adk_dir.exists():
        print("ADK agents directory not found. Please run setup_adk.py first.")
        sys.exit(1)
    
    # Check if .env file exists and has API keys
    env_file = adk_dir / ".env"
    if not env_file.exists():
        print(".env file not found. Please run setup_adk.py first.")
        sys.exit(1)
    
    # Check if API keys are configured
    with open(env_file, "r") as f:
        env_content = f.read()
        if "your_google_ai_studio_api_key_here" in env_content:
            print("Please update the API keys in adk_agents/.env file")
            sys.exit(1)
    
    print("Starting ADK Web UI...")
    print("Open http://localhost:8000 in your browser")
    print("Select 'video_generation_agent' from the dropdown")
    print("You can now test, debug, and showcase your video generation agent!")
    
    # Run ADK web from the project root
    subprocess.run(["adk", "web"], cwd=".")

if __name__ == "__main__":
    main()
"""
    
    with open("run_adk_web.py", "w") as f:
        f.write(run_web_content)
    
    # Make it executable
    os.chmod("run_adk_web.py", 0o755)
    print("Created run_adk_web.py script")
    
    # Create run_adk_terminal.py
    run_terminal_content = """#!/usr/bin/env python3
'''
Run ADK Terminal Interface for VideoAgent
'''

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to adk_agents directory
    adk_dir = Path("adk_agents")
    if not adk_dir.exists():
        print("ADK agents directory not found. Please run setup_adk.py first.")
        sys.exit(1)
    
    # Check if .env file exists and has API keys
    env_file = adk_dir / ".env"
    if not env_file.exists():
        print(".env file not found. Please run setup_adk.py first.")
        sys.exit(1)
    
    # Check if API keys are configured
    with open(env_file, "r") as f:
        env_content = f.read()
        if "your_google_ai_studio_api_key_here" in env_content:
            print("Please update the API keys in adk_agents/.env file")
            sys.exit(1)
    
    print("Starting ADK Terminal Interface...")
    print("You can now chat with your video generation agent!")
    print("Try: 'Generate a video about artificial intelligence'")
    print("Try: 'Check the system status'")
    print("Try: 'List generated videos'")
    
    # Run ADK terminal from the project root
    subprocess.run(["adk", "run", "adk_agents"], cwd=".")

if __name__ == "__main__":
    main()
"""
    
    with open("run_adk_terminal.py", "w") as f:
        f.write(run_terminal_content)
    
    # Make it executable
    os.chmod("run_adk_terminal.py", 0o755)
    print("Created run_adk_terminal.py script")

def main():
    """Main setup function"""
    print("Setting up Google ADK integration for VideoAgent...")
    print("=" * 50)
    
    # Create directory structure
    create_adk_structure()
    
    # Install dependencies
    install_dependencies()
    
    # Create run scripts
    create_run_script()
    
    print("\nADK setup complete!")
    print("\nNext steps:")
    print("1. Update API keys in adk_agents/.env file")
    print("2. Run 'python3 run_adk_web.py' for web interface")
    print("3. Run 'python3 run_adk_terminal.py' for terminal interface")
    print("\nADK Features you can now use:")
    print("- Interactive web UI for testing agents")
    print("- Terminal interface for quick testing")
    print("- Function call tracing and debugging")
    print("- Event inspection and logging")
    print("- Session management")
    print("- Audio/voice interaction (with compatible models)")

if __name__ == "__main__":
    main() 