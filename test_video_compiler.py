#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Video Compiler Agent
"""

import os
import sys
from agents.video_compiler_agent import VideoCompilerAgent
from moviepy import TextClip, ColorClip, CompositeVideoClip

def test_moviepy_textclip():
    """Test basic MoviePy TextClip functionality"""
    print("🧪 Testing basic MoviePy TextClip...")
    
    try:
        # Test basic TextClip creation
        text_clip = TextClip(text="Hello World", font_size=50, color='white')
        print("✅ Basic TextClip creation successful")
        
        # Test with duration
        text_clip = text_clip.with_duration(3)
        print("✅ TextClip with duration successful")
        
        # Test with position
        text_clip = text_clip.with_position('center')
        print("✅ TextClip with position successful")
        
        return True
        
    except Exception as e:
        print(f"❌ TextClip test failed: {e}")
        return False

def test_color_clip():
    """Test ColorClip functionality"""
    print("\n🧪 Testing ColorClip...")
    
    try:
        color_clip = ColorClip(size=(1920, 1080), color=(20, 20, 50), duration=5)
        print("✅ ColorClip creation successful")
        return True
        
    except Exception as e:
        print(f"❌ ColorClip test failed: {e}")
        return False

def test_composite_video():
    """Test CompositeVideoClip"""
    print("\n🧪 Testing CompositeVideoClip...")
    
    try:
        # Create background
        background = ColorClip(size=(1920, 1080), color=(20, 20, 50), duration=5)
        
        # Create text
        text = TextClip(text="Test Text", font_size=50, color='white').with_duration(5).with_position('center')
        
        # Composite
        composite = CompositeVideoClip([background, text])
        print("✅ CompositeVideoClip creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ CompositeVideoClip test failed: {e}")
        return False

def test_video_compiler_agent():
    """Test the VideoCompilerAgent"""
    print("\n🧪 Testing VideoCompilerAgent...")
    
    try:
        agent = VideoCompilerAgent()
        print("✅ VideoCompilerAgent initialization successful")
        
        # Test with sample scene data
        sample_scene = {
            "title": "Test Scene",
            "content": ["This is a test scene", "for debugging purposes"],
            "audio_file": "test_audio.mp3",  # This won't exist but we'll catch the error
            "illustration_type": "text_overlay"
        }
        
        # This should fail gracefully because audio file doesn't exist
        result = agent.create_scene_video(sample_scene, 0)
        print(f"Scene creation result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ VideoCompilerAgent test failed: {e}")
        return False

def create_dummy_audio():
    """Create a dummy audio file for testing"""
    print("\n🧪 Creating dummy audio file...")
    
    try:
        from moviepy import AudioFileClip
        import numpy as np
        from moviepy.audio.AudioClip import AudioClip
        
        # Create a simple tone
        def make_tone(duration=3, fps=22050, frequency=440):
            t = np.linspace(0, duration, int(fps * duration), False)
            tone = np.sin(frequency * 2 * np.pi * t)
            return tone
        
        # Create audio clip
        tone = make_tone(duration=3)
        audio_clip = AudioClip(lambda t: tone[int(t * 22050):int(t * 22050) + 1], duration=3, fps=22050)
        
        # Save to file
        os.makedirs("static/audio", exist_ok=True)
        audio_clip.write_audiofile("static/audio/test_audio.mp3", logger=None)
        print("✅ Dummy audio file created")
        
        return True
        
    except Exception as e:
        print(f"❌ Dummy audio creation failed: {e}")
        return False

def test_video_download():
    """Test video download functionality"""
    print("\n🧪 Testing video download functionality...")
    
    try:
        agent = VideoCompilerAgent()
        
        # Test with a sample video URL (using a placeholder)
        test_url = "https://httpbin.org/bytes/1024"  # This returns 1KB of data for testing
        test_path = "static/videos/test_download.mp4"
        
        # This should fail gracefully since it's not a real video
        result = agent.download_video_from_url(test_url, test_path)
        print(f"Download test result: {result}")
        
        # Test URL validation
        invalid_result = agent.download_video_from_url("invalid_url", test_path)
        print(f"Invalid URL test: {'✅ PASSED' if not invalid_result['success'] else '❌ FAILED'}")
        
        return True  # Test passes if it doesn't crash
        
    except Exception as e:
        print(f"❌ Video download test failed: {e}")
        return False

def test_complete_scene():
    """Test complete scene creation with real audio"""
    print("\n🧪 Testing complete scene creation...")
    
    try:
        agent = VideoCompilerAgent()
        
        # Create dummy audio first
        if not create_dummy_audio():
            return False
        
        # Test with sample scene data
        sample_scene = {
            "title": "Test Scene",
            "content": ["This is a test scene", "for debugging purposes"],
            "audio_file": "static/audio/test_audio.mp3",
            "illustration_type": "text_overlay"
        }
        
        result = agent.create_scene_video(sample_scene, 0)
        print(f"Complete scene creation result: {result}")
        
        if result["success"]:
            print(f"✅ Scene video created: {result['scene_video']}")
        else:
            print(f"❌ Scene creation failed: {result['error']}")
        
        return result["success"]
        
    except Exception as e:
        print(f"❌ Complete scene test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎬 Testing Video Compiler Agent Components")
    print("=" * 50)
    
    tests = [
        ("MoviePy TextClip", test_moviepy_textclip),
        ("ColorClip", test_color_clip),
        ("CompositeVideoClip", test_composite_video),
        ("VideoCompilerAgent", test_video_compiler_agent),
        ("Video Download", test_video_download),
        ("Complete Scene Creation", test_complete_scene)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 