#!/usr/bin/env python3
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
    
    # Check if virtual environment exists
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("Virtual environment not found. Please create a virtual environment and install dependencies.")
        sys.exit(1)
    
    print("Starting ADK Web UI...")
    print("Open http://localhost:8000 in your browser")
    print("Select 'video_generation_agent' from the dropdown")
    print("You can now test, debug, and showcase your video generation agent!")
    
    # Run ADK web from the project root with virtual environment activated
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate.bat"
        cmd = f"{activate_script} && adk web"
        subprocess.run(cmd, shell=True, cwd=".")
    else:  # Unix/MacOS
        activate_script = "venv/bin/activate"
        cmd = f"source {activate_script} && adk web"
        subprocess.run(cmd, shell=True, cwd=".")

if __name__ == "__main__":
    main()
