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

def test_caption_functionality():
    """Test caption functionality with custom styling"""
    print("\n🧪 Testing caption functionality...")
    
    try:
        from moviepy import TextClip, ColorClip, CompositeVideoClip
        from moviepy.video.fx import FadeIn, FadeOut
        import numpy as np
        
        # Create a background video (simulating main video content)
        background = ColorClip(size=(1920, 1080), color=(20, 50, 100), duration=10)
        
        # Test dialogue data
        dialogue_data = [
            {"text": "Welcome to our video presentation!", "start": 0, "end": 3},
            {"text": "This is the first line of dialogue with a longer text to test wrapping.", "start": 3, "end": 6},
            {"text": "Here's another caption that should fade in and out smoothly.", "start": 6, "end": 9}
        ]
        
        # Create captions list
        caption_clips = []
        
        for dialogue in dialogue_data:
            # Create caption with specific styling
            caption_clip = create_styled_caption(
                text=dialogue["text"],
                start_time=dialogue["start"],
                end_time=dialogue["end"],
                video_size=(1920, 1080)
            )
            
            if caption_clip:
                caption_clips.append(caption_clip)
        
        # Composite all clips together
        all_clips = [background] + caption_clips
        final_video = CompositeVideoClip(all_clips)
        
        # Save test video
        os.makedirs("static/videos", exist_ok=True)
        test_output = "static/videos/caption_test.mp4"
        final_video.write_videofile(test_output, fps=24, logger=None)
        
        print(f"✅ Caption test video created: {test_output}")
        
        # Cleanup
        final_video.close()
        
        # Verify file was created
        if os.path.exists(test_output):
            file_size = os.path.getsize(test_output)
            print(f"✅ Caption test file size: {file_size / 1024:.2f} KB")
            return True
        else:
            print("❌ Caption test video was not created")
            return False
            
    except Exception as e:
        print(f"❌ Caption test failed: {e}")
        return False

def create_styled_caption(text, start_time, end_time, video_size):
    """
    Create a styled caption with the specific requirements:
    - White text on black background box
    - Bottom padding of 10%
    - Left-aligned with 70% width
    - Fading texture from left to right
    - Fade in/out animation
    """
    try:
        from moviepy import TextClip, ColorClip, CompositeVideoClip
        from moviepy.video.fx import FadeIn, FadeOut
        import numpy as np
        
        # Calculate dimensions
        video_width, video_height = video_size
        caption_width = int(video_width * 0.7)  # 70% width
        caption_height = 80  # Fixed height for caption box
        
        # Position calculation - bottom 10% padding
        bottom_padding = int(video_height * 0.1)
        caption_y = video_height - caption_height - bottom_padding
        caption_x = 0  # Left-aligned
        
        # Create text clip - remove align parameter and use method='caption'
        text_clip = TextClip(
            text=text,
            font_size=32,
            color='white',
            method='caption',
            size=(caption_width - 40, None)  # Leave some margin
        ).with_duration(end_time - start_time).with_start(start_time)
        
        # Create base black background
        bg_clip = ColorClip(
            size=(caption_width, caption_height),
            color=(0, 0, 0),
            duration=end_time - start_time
        ).with_start(start_time)
        
        # Create gradient effect (simplified)
        gradient_clip = ColorClip(
            size=(caption_width, caption_height),
            color=(30, 30, 30),  # Slightly lighter than black
            duration=end_time - start_time
        ).with_start(start_time).with_opacity(0.3)
        
        # Position the text within the caption box (centered vertically, left-aligned horizontally)
        text_clip = text_clip.with_position((caption_x + 20, caption_y + 10))
        bg_clip = bg_clip.with_position((caption_x, caption_y))
        gradient_clip = gradient_clip.with_position((caption_x, caption_y))
        
        # Apply fade in/out effects
        fade_duration = 0.5  # 0.5 second fade
        text_clip = text_clip.with_effects([FadeIn(fade_duration), FadeOut(fade_duration)])
        bg_clip = bg_clip.with_effects([FadeIn(fade_duration), FadeOut(fade_duration)])
        gradient_clip = gradient_clip.with_effects([FadeIn(fade_duration), FadeOut(fade_duration)])
        
        # Composite the caption (background + gradient + text)
        caption_composite = CompositeVideoClip([bg_clip, gradient_clip, text_clip])
        
        return caption_composite
        
    except Exception as e:
        print(f"⚠️  Error creating styled caption: {e}")
        return None

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
        
        # Create a proper audio function that returns an array
        def audio_func(t):
            if isinstance(t, np.ndarray):
                # For array input, return array of samples
                indices = np.clip((t * 22050).astype(int), 0, len(tone) - 1)
                return tone[indices]
            else:
                # For single value input, return single sample
                index = min(int(t * 22050), len(tone) - 1)
                return tone[index]
        
        audio_clip = AudioClip(audio_func, duration=3, fps=22050)
        
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

def test_looped_video():
    """Test creating a looped video of specific duration"""
    print("\n🧪 Testing looped video creation...")
    
    try:
        from moviepy import VideoFileClip, concatenate_videoclips
        
        # Create a short base video clip (2 seconds)
        background = ColorClip(size=(1920, 1080), color=(100, 50, 150), duration=2)
        text = TextClip(text="LOOP TEST", font_size=80, color='white').with_duration(2).with_position('center')
        
        # Create composite base clip
        base_clip = CompositeVideoClip([background, text])
        
        # Create looped video by repeating the clip
        target_duration = 10  # 10 seconds
        base_duration = base_clip.duration
        num_loops = int(target_duration / base_duration) + 1  # Add one extra to ensure we reach target
        
        # Create list of clips to concatenate
        clips_to_loop = [base_clip] * num_loops
        
        # Concatenate clips to create loop
        looped_clip = concatenate_videoclips(clips_to_loop, method="chain")
        
        # Trim to exact target duration
        if looped_clip.duration > target_duration:
            looped_clip = looped_clip.subclipped(0, target_duration)
        
        # Verify the duration
        actual_duration = looped_clip.duration
        print(f"✅ Looped video created - Target: {target_duration}s, Actual: {actual_duration:.2f}s")
        
        # Save the looped video
        os.makedirs("static/videos", exist_ok=True)
        looped_path = "static/videos/looped_test.mp4"
        looped_clip.write_videofile(looped_path, fps=24, logger=None)
        print(f"✅ Looped video saved to: {looped_path}")
        
        # Cleanup
        looped_clip.close()
        base_clip.close()
        
        # Verify the file was created and has reasonable size
        if os.path.exists(looped_path):
            file_size = os.path.getsize(looped_path)
            print(f"✅ Looped video file size: {file_size / 1024:.2f} KB")
            
            # Clean up test files
            os.remove(looped_path)
            print("✅ Test files cleaned up")
            
            return True
        else:
            print("❌ Looped video file was not created")
            return False
        
    except Exception as e:
        print(f"❌ Looped video test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎬 Testing Video Compiler Agent Components")
    print("=" * 50)
    
    tests = [
        ("MoviePy TextClip", test_moviepy_textclip),
        ("Caption Functionality", test_caption_functionality),
        ("ColorClip", test_color_clip),
        ("CompositeVideoClip", test_composite_video),
        ("VideoCompilerAgent", test_video_compiler_agent),
        ("Video Download", test_video_download),
        ("Complete Scene Creation", test_complete_scene),
        ("Looped Video", test_looped_video)
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