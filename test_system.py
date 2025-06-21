#!/usr/bin/env python3
"""
Test script to verify the video generation agent system works correctly
"""

import os
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from google.adk.agents import LlmAgent
        print("✅ Google ADK imported successfully")
    except ImportError as e:
        print(f"❌ Google ADK import failed: {e}")
        return False
    
    try:
        from agents.video_script_agent import VideoScriptAgent
        print("✅ VideoScriptAgent imported successfully")
    except ImportError as e:
        print(f"❌ VideoScriptAgent import failed: {e}")
        return False
    
    try:
        from agents.audio_generation_agent import AudioGenerationAgent
        print("✅ AudioGenerationAgent imported successfully")
    except ImportError as e:
        print(f"❌ AudioGenerationAgent import failed: {e}")
        return False
        
    try:
        from agents.video_illustration_agent import VideoIllustrationAgent
        print("✅ VideoIllustrationAgent imported successfully")
    except ImportError as e:
        print(f"❌ VideoIllustrationAgent import failed: {e}")
        return False
        
    try:
        from agents.manim_illustration_agent import ManimIllustrationAgent
        print("✅ ManimIllustrationAgent imported successfully")
    except ImportError as e:
        print(f"❌ ManimIllustrationAgent import failed: {e}")
        return False
        
    try:
        from agents.video_compiler_agent import VideoCompilerAgent
        print("✅ VideoCompilerAgent imported successfully")
    except ImportError as e:
        print(f"❌ VideoCompilerAgent import failed: {e}")
        return False
        
    try:
        from video_generation_orchestrator import VideoGenerationOrchestrator
        print("✅ VideoGenerationOrchestrator imported successfully")
    except ImportError as e:
        print(f"❌ VideoGenerationOrchestrator import failed: {e}")
        return False
        
    return True

def test_agent_initialization():
    """Test that agents can be initialized"""
    print("\n🤖 Testing agent initialization...")
    
    try:
        from agents.video_script_agent import VideoScriptAgent
        agent = VideoScriptAgent("dummy_key")
        print(f"✅ VideoScriptAgent initialized: {agent.name}")
    except Exception as e:
        print(f"❌ VideoScriptAgent initialization failed: {e}")
        return False
        
    try:
        from agents.audio_generation_agent import AudioGenerationAgent
        agent = AudioGenerationAgent("dummy_key")
        print(f"✅ AudioGenerationAgent initialized: {agent.name}")
    except Exception as e:
        print(f"❌ AudioGenerationAgent initialization failed: {e}")
        return False
        
    try:
        from agents.video_illustration_agent import VideoIllustrationAgent
        agent = VideoIllustrationAgent("dummy_key")
        print(f"✅ VideoIllustrationAgent initialized: {agent.name}")
    except Exception as e:
        print(f"❌ VideoIllustrationAgent initialization failed: {e}")
        return False
        
    try:
        from agents.manim_illustration_agent import ManimIllustrationAgent
        agent = ManimIllustrationAgent("dummy_key")
        print(f"✅ ManimIllustrationAgent initialized: {agent.name}")
    except Exception as e:
        print(f"❌ ManimIllustrationAgent initialization failed: {e}")
        return False
        
    try:
        from agents.video_compiler_agent import VideoCompilerAgent
        agent = VideoCompilerAgent()
        print(f"✅ VideoCompilerAgent initialized: {agent.name}")
    except Exception as e:
        print(f"❌ VideoCompilerAgent initialization failed: {e}")
        return False
        
    return True

def test_dependencies():
    """Test that all dependencies are available"""
    print("\n📦 Testing dependencies...")
    
    dependencies = [
        ('google.generativeai', 'Google Gemini API client'),
        ('moviepy', 'MoviePy video editing'),
        ('manim', 'Manim animation library'),
        ('gtts', 'Google Text-to-Speech'),
        ('cloudscraper', 'CloudScraper web scraping'),
        ('requests', 'HTTP requests'),
        ('json', 'JSON handling'),
        ('os', 'Operating system interface'),
        ('subprocess', 'Process management'),
        ('random', 'Random number generation'),
        ('string', 'String utilities'),
    ]
    
    failed_deps = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - {description}")
        except ImportError as e:
            print(f"❌ {dep} - {description} (Error: {e})")
            failed_deps.append(dep)
    
    return len(failed_deps) == 0

def main():
    """Run all tests"""
    print("🎬 Video Generation Agent System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Agent Initialization Tests", test_agent_initialization),
        ("Dependency Tests", test_dependencies)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if not test_func():
            print(f"❌ {test_name} failed!")
            all_passed = False
        else:
            print(f"✅ {test_name} passed!")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in a .env file")
        print("2. Run: python3 main.py")
        print("3. Or: python3 video_generation_orchestrator.py 'your topic'")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 