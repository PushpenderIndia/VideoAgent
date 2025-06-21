#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Video Generation Agent System
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False
    return True

def setup_environment():
    """Setup environment file"""
    print("🔧 Setting up environment...")
    
    env_example = ".env.example"
    env_file = ".env"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            # Copy example to .env
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Created {env_file} from {env_example}")
            print("⚠️  Please edit .env file and add your API keys:")
            print("   - OPENAI_API_KEY")
            print("   - ELEVEN_LABS_API")
        else:
            print(f"❌ {env_example} not found")
            return False
    else:
        print(f"✅ {env_file} already exists")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "static",
        "static/audio",
        "static/videos", 
        "static/manim_outputs",
        "static/compiled_videos",
        "agents"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def check_system_dependencies():
    """Check for system dependencies"""
    print("🔍 Checking system dependencies...")
    
    # Check for ffmpeg (required by moviepy)
    try:
        subprocess.run(["ffmpeg", "-version"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        print("✅ ffmpeg found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  ffmpeg not found - required for video processing")
        print("   Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)")
    
    # Check for manim dependencies
    try:
        import manim
        print("✅ Manim available")
    except ImportError:
        print("⚠️  Manim not available - install with: pip install manim")
    
    return True

def main():
    """Main setup function"""
    print("🎬 Video Generation Agent System Setup")
    print("=" * 40)
    
    steps = [
        ("Installing requirements", install_requirements),
        ("Setting up environment", setup_environment), 
        ("Creating directories", create_directories),
        ("Checking system dependencies", check_system_dependencies)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python main.py")
    print("3. Or: python video_generation_orchestrator.py 'your topic'")
    
    return True

if __name__ == "__main__":
    main() 