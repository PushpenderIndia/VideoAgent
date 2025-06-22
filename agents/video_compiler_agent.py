from google.adk.agents import LlmAgent
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
from moviepy.video.fx import Resize, FadeIn, FadeOut
import os
import json
import requests
import random
import numpy as np
from typing import List, Dict

class VideoCompilerAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="VideoCompilerAgent",
            description="Compiles video scenes using MoviePy to create final video"
        )
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize configuration after parent initialization"""
        self.__dict__['output_dir'] = "static/compiled_videos"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize transition effects (simplified for compatibility)
        self.__dict__['transition_effects'] = [
            'crossfade',
            'fade_to_black',
            'zoom_in',
            'zoom_out',
            'quick_fade'
        ]
    
    def _create_looped_video(self, video_clip, target_duration):
        """
        Create a looped video from a clip to match target duration
        
        Args:
            video_clip: The video clip to loop
            target_duration (float): Target duration in seconds
            
        Returns:
            VideoClip: Looped video clip
        """
        try:
            if video_clip.duration >= target_duration:
                # If video is already long enough, just trim it
                return video_clip.subclipped(0, target_duration)
            
            # Calculate how many loops we need
            num_loops = int(target_duration / video_clip.duration) + 1
            
            # Create list of clips to concatenate
            clips_to_loop = [video_clip] * num_loops
            
            # Concatenate clips to create loop
            looped_clip = concatenate_videoclips(clips_to_loop, method="chain")
            
            # Trim to exact target duration
            if looped_clip.duration > target_duration:
                looped_clip = looped_clip.subclipped(0, target_duration)
            
            return looped_clip
            
        except Exception as e:
            print(f"⚠️  Error creating looped video: {e}")
            # Fallback: just return the original clip trimmed or extended with a freeze frame
            if video_clip.duration >= target_duration:
                return video_clip.subclipped(0, target_duration)
            else:
                # Extend with freeze frame
                last_frame = video_clip.subclipped(video_clip.duration - 0.1, video_clip.duration)
                extension_duration = target_duration - video_clip.duration
                extended_frame = last_frame.with_duration(extension_duration)
                return concatenate_videoclips([video_clip, extended_frame], method="chain")
    
    def _select_dynamic_transition(self, prev_scene_data: dict, next_scene_data: dict, transition_index: int) -> str:
        """
        Dynamically select transition effect based on scene content and context
        
        Args:
            prev_scene_data (dict): Previous scene data
            next_scene_data (dict): Next scene data  
            transition_index (int): Index of the transition
            
        Returns:
            str: Selected transition effect name
        """
        try:
            # Analyze scene content to choose appropriate transition
            prev_content = " ".join(prev_scene_data.get("content", [])).lower()
            next_content = " ".join(next_scene_data.get("content", [])).lower()
            
            # Action/movement keywords suggest zoom transitions
            action_keywords = ['move', 'run', 'walk', 'travel', 'journey', 'go', 'arrive', 'leave', 'fast', 'quick']
            if any(keyword in prev_content or keyword in next_content for keyword in action_keywords):
                return random.choice(['zoom_in', 'zoom_out', 'quick_fade'])
            
            # Dramatic/emotional keywords suggest fade transitions
            dramatic_keywords = ['dramatic', 'emotional', 'sad', 'happy', 'surprise', 'shock', 'reveal']
            if any(keyword in prev_content or keyword in next_content for keyword in dramatic_keywords):
                return random.choice(['fade_to_black', 'crossfade'])
            
            # Time-related keywords suggest quick transitions
            time_keywords = ['time', 'then', 'next', 'after', 'before', 'meanwhile', 'suddenly']
            if any(keyword in prev_content or keyword in next_content for keyword in time_keywords):
                return 'quick_fade'
            
            # Scale/size keywords suggest zoom transitions  
            scale_keywords = ['big', 'small', 'large', 'tiny', 'huge', 'grow', 'shrink', 'expand']
            if any(keyword in prev_content or keyword in next_content for keyword in scale_keywords):
                return random.choice(['zoom_in', 'zoom_out'])
                
            # Default: select based on transition index for variety
            if transition_index % 4 == 0:
                return 'crossfade'
            elif transition_index % 4 == 1:
                return 'zoom_in'
            elif transition_index % 4 == 2:
                return 'fade_to_black'
            else:
                return 'quick_fade'
                
        except Exception as e:
            print(f"⚠️  Error in transition selection: {e}")
            return 'crossfade'  # Safe fallback
    
    def _apply_transition_effect(self, clip1: VideoFileClip, clip2: VideoFileClip, 
                                transition_type: str, duration: float = 1.0) -> List[VideoFileClip]:
        """
        Apply transition effect between two video clips
        
        Args:
            clip1 (VideoFileClip): First video clip
            clip2 (VideoFileClip): Second video clip
            transition_type (str): Type of transition effect
            duration (float): Duration of transition in seconds
            
        Returns:
            List[VideoFileClip]: List of clips with transition applied
        """
        try:
            if transition_type == 'crossfade':
                # Cross-fade transition
                clip1_fade = clip1.with_effects([FadeOut(duration)])
                clip2_fade = clip2.with_effects([FadeIn(duration)])
                return [clip1_fade, clip2_fade]
                
            elif transition_type == 'fade_to_black':
                # Fade to black transition
                black_clip = ColorClip(size=clip1.size, color=(0,0,0), duration=duration/2)
                # Add silent audio to black clip to maintain audio continuity
                from moviepy.audio.AudioClip import AudioClip
                silent_audio = AudioClip(lambda t: 0, duration=duration/2, fps=22050)
                black_clip = black_clip.with_audio(silent_audio)
                
                clip1_fade = clip1.with_effects([FadeOut(duration/2)])
                clip2_fade = clip2.with_effects([FadeIn(duration/2)])
                return [clip1_fade, black_clip, clip2_fade]
                
            elif transition_type == 'zoom_in':
                # Zoom in transition - apply zoom to end of first clip
                zoom_duration = min(duration, clip1.duration)
                clip1_end = clip1.subclipped(max(0, clip1.duration - zoom_duration), clip1.duration)
                clip1_start = clip1.subclipped(0, max(0, clip1.duration - zoom_duration))
                
                clip1_zoomed = clip1_end.resized(lambda t: 1 + 0.3 * (t / zoom_duration))
                
                if clip1_start.duration > 0:
                    clip1_final = concatenate_videoclips([clip1_start, clip1_zoomed], method="chain")
                else:
                    clip1_final = clip1_zoomed
                    
                clip2_normal = clip2.with_effects([FadeIn(duration)])
                return [clip1_final, clip2_normal]
                
            elif transition_type == 'zoom_out':
                # Zoom out transition - apply zoom to end of first clip 
                zoom_duration = min(duration, clip1.duration)
                clip1_end = clip1.subclipped(max(0, clip1.duration - zoom_duration), clip1.duration)
                clip1_start = clip1.subclipped(0, max(0, clip1.duration - zoom_duration))
                
                clip1_zoomed = clip1_end.resized(lambda t: max(0.7, 1 - 0.3 * (t / zoom_duration)))
                
                if clip1_start.duration > 0:
                    clip1_final = concatenate_videoclips([clip1_start, clip1_zoomed], method="chain")
                else:
                    clip1_final = clip1_zoomed
                    
                clip2_normal = clip2.with_effects([FadeIn(duration)])
                return [clip1_final, clip2_normal]
                
            elif transition_type == 'quick_fade':
                # Quick fade transition (shorter duration)
                quick_duration = duration * 0.5
                clip1_fade = clip1.with_effects([FadeOut(quick_duration)])
                clip2_fade = clip2.with_effects([FadeIn(quick_duration)])
                return [clip1_fade, clip2_fade]
                
            else:
                # Default crossfade
                clip1_fade = clip1.with_effects([FadeOut(duration)])
                clip2_fade = clip2.with_effects([FadeIn(duration)]) 
                return [clip1_fade, clip2_fade]
                
        except Exception as e:
            print(f"⚠️  Error applying transition {transition_type}: {e}")
            # Fallback to simple crossfade
            clip1_fade = clip1.with_effects([FadeOut(duration)])
            clip2_fade = clip2.with_effects([FadeIn(duration)])
            return [clip1_fade, clip2_fade]
    
    def create_styled_caption(self, text, start_time, end_time, video_size):
        """
        Create a styled caption with specific design requirements:
        - White text on black background box
        - Bottom padding of 10%
        - Left-aligned with 70% width
        - Fading texture from left to right
        - Fade in/out animation
        
        Args:
            text (str): Caption text
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            video_size (tuple): Video dimensions (width, height)
            
        Returns:
            CompositeVideoClip: Styled caption clip
        """
        try:
            # Calculate dimensions
            video_width, video_height = video_size
            caption_width = int(video_width * 0.7)  # 70% width
            caption_height = 80  # Fixed height for caption box
            
            # Position calculation - bottom 10% padding
            bottom_padding = int(video_height * 0.1)
            caption_y = video_height - caption_height - bottom_padding
            caption_x = 0  # Left-aligned
            
            # Create text clip - remove align parameter for compatibility
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
            
            # Create gradient effect (simplified for better compatibility)
            gradient_clip = ColorClip(
                size=(caption_width, caption_height),
                color=(30, 30, 30),  # Slightly lighter than black for gradient effect
                duration=end_time - start_time
            ).with_start(start_time).with_opacity(0.3)
            
            # Position all elements
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
    
    def add_captions_to_video(self, video_clip, dialogue_data, video_size=None):
        """
        Add styled captions to a video clip based on dialogue data
        
        Args:
            video_clip: The main video clip
            dialogue_data (list): List of dialogue objects with 'text', 'start', 'end' keys
            video_size (tuple): Video dimensions (width, height). If None, uses video_clip.size
            
        Returns:
            CompositeVideoClip: Video with captions added
        """
        try:
            if not dialogue_data:
                return video_clip
            
            # Get video size
            if video_size is None:
                video_size = video_clip.size
            
            # Create caption clips
            caption_clips = []
            
            for dialogue in dialogue_data:
                caption_clip = self.create_styled_caption(
                    text=dialogue.get("text", ""),
                    start_time=dialogue.get("start", 0),
                    end_time=dialogue.get("end", 1),
                    video_size=video_size
                )
                
                if caption_clip:
                    caption_clips.append(caption_clip)
            
            # Composite video with captions
            if caption_clips:
                all_clips = [video_clip] + caption_clips
                return CompositeVideoClip(all_clips)
            else:
                return video_clip
                
        except Exception as e:
            print(f"⚠️  Error adding captions to video: {e}")
            return video_clip
    
    def extract_dialogue_from_content(self, content, audio_duration):
        """
        Extract dialogue data from scene content for caption generation
        
        Args:
            content (list): List of content strings
            audio_duration (float): Duration of audio in seconds
            
        Returns:
            list: List of dialogue objects with timing information
        """
        try:
            dialogue_data = []
            
            if not content:
                return dialogue_data
            
            # Calculate timing for each content piece
            total_lines = len(content)
            time_per_line = audio_duration / total_lines if total_lines > 0 else audio_duration
            
            for i, text in enumerate(content):
                start_time = i * time_per_line
                end_time = min((i + 1) * time_per_line, audio_duration)
                
                dialogue_data.append({
                    "text": text.strip(),
                    "start": start_time,
                    "end": end_time
                })
            
            return dialogue_data
            
        except Exception as e:
            print(f"⚠️  Error extracting dialogue from content: {e}")
            return []
    
    def create_scene_video(self, scene_data: dict, scene_index: int, video_illustration_agent=None) -> dict:
        """
        Create a video clip for a single scene
        
        Args:
            scene_data (dict): Scene data with audio, video/illustration files
            scene_index (int): Index of the scene
            video_illustration_agent: VideoIllustrationAgent instance for unique video selection
            
        Returns:
            dict: Result with scene video clip path
        """
        try:
            # Load audio clip to get duration
            if not os.path.exists(scene_data["audio_file"]):
                return {
                    "success": False,
                    "error": f"Audio file not found: {scene_data['audio_file']}",
                    "scene_index": scene_index
                }
            
            audio_clip = AudioFileClip(scene_data["audio_file"])
            audio_duration = audio_clip.duration
            
            # Create video clip based on available media
            if scene_data.get("manim_video") and os.path.exists(scene_data["manim_video"]):
                # Use Manim-generated video
                video_clip = VideoFileClip(scene_data["manim_video"])
                
                # Adjust video duration to match audio
                video_clip = self._create_looped_video(video_clip, audio_duration)
                    
            elif scene_data.get("video_url"):
                # Download and use Getty Images video
                video_url = scene_data["video_url"]
                downloaded_video_path = os.path.join("static", "videos", f"downloaded_{scene_index}.mp4")
                
                # Download the video
                download_result = self.download_video_from_url(video_url, downloaded_video_path)
                
                if download_result["success"]:
                    # Use downloaded video
                    try:
                        video_clip = VideoFileClip(download_result["file_path"])
                        
                        # Adjust video duration to match audio
                        video_clip = self._create_looped_video(video_clip, audio_duration)
                        
                        # Resize to standard dimensions if needed
                        if video_clip.size != (1920, 1080):
                            video_clip = video_clip.resized((1920, 1080))
                        
                        print(f"✅ Using downloaded video: {download_result['message']}")
                        
                    except Exception as e:
                        print(f"⚠️  Error processing downloaded video: {e}")
                        # Try to get a unique video as fallback
                        if video_illustration_agent and scene_data.get("content"):
                            content = " ".join(scene_data.get("content", []))
                            scene_title = scene_data.get("title", "")
                            unique_video_result = video_illustration_agent.get_unique_video_for_scene(content, scene_index, scene_title)
                            if unique_video_result["success"]:
                                print(f"🔄 Retrying with unique video for scene {scene_index} using title: {scene_title}")
                                scene_data["video_url"] = unique_video_result["video_url"]
                                return self.create_scene_video(scene_data, scene_index, video_illustration_agent)
                        
                        # Final fallback to colored background with title
                        video_clip = ColorClip(size=(1920, 1080), color=(0, 50, 100), duration=audio_duration)
                        
                        title_text = TextClip(
                            text=scene_data.get("title", f"Scene {scene_index + 1}"),
                            font_size=60,
                            color='white'
                        ).with_position('center').with_duration(audio_duration)
                        
                        video_clip = CompositeVideoClip([video_clip, title_text])
                else:
                    print(f"⚠️  Video download failed: {download_result['message']}")
                    
                    # Try to get a unique video as fallback
                    if video_illustration_agent and scene_data.get("content"):
                        content = " ".join(scene_data.get("content", []))
                        scene_title = scene_data.get("title", "")
                        unique_video_result = video_illustration_agent.get_unique_video_for_scene(content, scene_index, scene_title)
                        if unique_video_result["success"]:
                            print(f"🔄 Found alternative unique video for scene {scene_index} using title: {scene_title}")
                            scene_data["video_url"] = unique_video_result["video_url"]
                            return self.create_scene_video(scene_data, scene_index, video_illustration_agent)
                    
                    # Fallback to colored background with title
                    video_clip = ColorClip(size=(1920, 1080), color=(0, 50, 100), duration=audio_duration)
                    
                    title_text = TextClip(
                        text=scene_data.get("title", f"Scene {scene_index + 1}"),
                        font_size=60,
                        color='white'
                    ).with_position('center').with_duration(audio_duration)
                    
                    video_clip = CompositeVideoClip([video_clip, title_text])
                
            else:
                # Try to get a unique video using the video illustration agent
                if video_illustration_agent and scene_data.get("content"):
                    content = " ".join(scene_data.get("content", []))
                    scene_title = scene_data.get("title", "")
                    unique_video_result = video_illustration_agent.get_unique_video_for_scene(content, scene_index, scene_title)
                    
                    if unique_video_result["success"]:
                        print(f"🎯 Found unique video for scene {scene_index} using title-based search: {scene_title}")
                        scene_data["video_url"] = unique_video_result["video_url"]
                        return self.create_scene_video(scene_data, scene_index, video_illustration_agent)
                
                # Create a simple background with text
                video_clip = ColorClip(size=(1920, 1080), color=(20, 20, 50), duration=audio_duration)
                
                # Add scene content as text overlay
                content_text = "\n".join(scene_data.get("content", ["No content"]))
                if len(content_text) > 200:
                    content_text = content_text[:200] + "..."
                
                text_clip = TextClip(
                    text=content_text,
                    font_size=40,
                    color='white',
                    size=(1600, None),
                    method='caption'
                ).with_position('center').with_duration(audio_duration)
                
                video_clip = CompositeVideoClip([video_clip, text_clip])
            
            # Add captions if content is available
            if scene_data.get("content") and scene_data.get("add_captions", True):
                dialogue_data = self.extract_dialogue_from_content(
                    scene_data["content"], 
                    audio_duration
                )
                
                if dialogue_data:
                    print(f"📝 Adding {len(dialogue_data)} captions to scene {scene_index}")
                    video_clip = self.add_captions_to_video(
                        video_clip, 
                        dialogue_data, 
                        video_size=(1920, 1080)
                    )
            
            # Set audio
            final_clip = video_clip.with_audio(audio_clip)
            
            # Save scene video
            scene_output = os.path.join(self.output_dir, f"scene_{scene_index:02d}.mp4")
            final_clip.write_videofile(
                scene_output,
                fps=24,
                audio_codec='aac',
                codec='libx264',
                logger=None
            )
            
            # Clean up
            audio_clip.close()
            video_clip.close()
            final_clip.close()
            
            return {
                "success": True,
                "scene_video": scene_output,
                "scene_index": scene_index,
                "duration": audio_duration,
                "message": f"Scene {scene_index} video created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "scene_index": scene_index,
                "message": f"Failed to create scene {scene_index} video"
            }
    
    def download_video_from_url(self, video_url: str, output_path: str, max_file_size_mb: int = 50) -> dict:
        """
        Download video from URL (Getty Images) with comprehensive error handling
        
        Args:
            video_url (str): URL of the video to download
            output_path (str): Path to save the downloaded video
            max_file_size_mb (int): Maximum file size in MB to download
            
        Returns:
            dict: Result of download operation
        """
        try:
            import requests
            import time
            from urllib.parse import urlparse
            
            # Validate URL
            if not video_url or not video_url.startswith(('http://', 'https://')):
                return {
                    "success": False,
                    "error": "Invalid video URL",
                    "message": "URL must start with http:// or https://"
                }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Set headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Start download with stream=True for large files
            print(f"🔄 Downloading video from: {video_url}")
            response = requests.get(video_url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'video' not in content_type and 'application/octet-stream' not in content_type:
                return {
                    "success": False,
                    "error": f"Invalid content type: {content_type}",
                    "message": "URL does not point to a video file"
                }
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length:
                file_size_mb = int(content_length) / (1024 * 1024)
                if file_size_mb > max_file_size_mb:
                    return {
                        "success": False,
                        "error": f"File too large: {file_size_mb:.1f}MB > {max_file_size_mb}MB",
                        "message": "Video file exceeds maximum allowed size"
                    }
                print(f"📁 File size: {file_size_mb:.1f}MB")
            
            # Download with progress tracking
            total_size = int(content_length) if content_length else 0
            downloaded_size = 0
            start_time = time.time()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress for larger files
                        if total_size > 0 and downloaded_size % (1024 * 1024) == 0:  # Every MB
                            progress = (downloaded_size / total_size) * 100
                            print(f"📥 Progress: {progress:.1f}%")
            
            download_time = time.time() - start_time
            final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            # Validate downloaded file
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                return {
                    "success": False,
                    "error": "Downloaded file is empty or missing",
                    "message": "Download completed but file is invalid"
                }
            
            # Try to validate it's a proper video file using MoviePy
            try:
                from moviepy import VideoFileClip
                test_clip = VideoFileClip(output_path)
                duration = test_clip.duration
                test_clip.close()
                
                print(f"✅ Video validation successful - Duration: {duration:.1f}s")
                
            except Exception as e:
                # If MoviePy can't read it, it's probably not a valid video
                os.remove(output_path)  # Clean up invalid file
                return {
                    "success": False,
                    "error": f"Invalid video file: {str(e)}",
                    "message": "Downloaded file is not a valid video"
                }
            
            return {
                "success": True,
                "file_path": output_path,
                "file_size_mb": final_size_mb,
                "download_time_seconds": download_time,
                "video_duration": duration,
                "message": f"Video downloaded successfully ({final_size_mb:.1f}MB in {download_time:.1f}s)"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "message": "Failed to download video due to network issues"
            }
        except Exception as e:
            # Clean up partially downloaded file
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to download video"
            }
    
    def compile_final_video(self, scenes_data: list, output_filename: str = "final_video.mp4", video_illustration_agent=None) -> dict:
        """
        Compile all scene videos into final video
        
        Args:
            scenes_data (list): List of scene data dictionaries
            output_filename (str): Name of the final output video
            video_illustration_agent: VideoIllustrationAgent instance for unique video selection
            
        Returns:
            dict: Result with final video path
        """
        try:
            scene_clips = []
            total_duration = 0
            self._transitions_log = []  # Track transitions used
            
            # Reset used videos if agent is provided
            if video_illustration_agent:
                video_illustration_agent.reset_used_videos()
                print("🔄 Reset video tracker for unique video selection")
            
            # Create individual scene videos
            for i, scene_data in enumerate(scenes_data):
                scene_result = self.create_scene_video(scene_data, i, video_illustration_agent)
                
                if scene_result["success"]:
                    scene_clips.append(scene_result["scene_video"])
                    total_duration += scene_result["duration"]
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create scene {i}: {scene_result['error']}",
                        "message": "Scene creation failed"
                    }
            
            # Load all scene video clips and apply transitions
            video_clips = []
            for scene_path in scene_clips:
                clip = VideoFileClip(scene_path)
                video_clips.append(clip)
            
            # Apply dynamic transitions between clips
            if len(video_clips) > 1:
                transitioned_clips = []
                
                # Add first clip as-is
                transitioned_clips.append(video_clips[0])
                
                # Apply transitions between consecutive clips
                for i in range(1, len(video_clips)):
                    prev_scene_data = scenes_data[i-1] if i-1 < len(scenes_data) else {}
                    current_scene_data = scenes_data[i] if i < len(scenes_data) else {}
                    
                    # Select dynamic transition
                    transition_type = self._select_dynamic_transition(
                        prev_scene_data, current_scene_data, i-1
                    )
                    
                    # Log the transition
                    self._transitions_log.append({
                        "from_scene": i-1,
                        "to_scene": i,
                        "transition_type": transition_type,
                        "reason": f"Selected based on content analysis"
                    })
                    
                    print(f"🎬 Applying {transition_type} transition between scene {i-1} and {i}")
                    
                    # Apply transition effect
                    prev_clip = transitioned_clips[-1] if transitioned_clips else video_clips[i-1]
                    current_clip = video_clips[i]
                    
                    # Create transition with 1 second duration
                    transition_clips = self._apply_transition_effect(
                        prev_clip, current_clip, transition_type, duration=1.0
                    )
                    
                    # Replace last clip with transitioned version and add current clip
                    if len(transition_clips) == 2:
                        # Standard transition (crossfade, slide, etc.)
                        transitioned_clips[-1] = transition_clips[0]  # Replace previous clip
                        transitioned_clips.append(transition_clips[1])  # Add current clip
                    elif len(transition_clips) == 3:
                        # Fade to black transition
                        transitioned_clips[-1] = transition_clips[0]  # Replace previous clip
                        transitioned_clips.append(transition_clips[1])  # Add black clip
                        transitioned_clips.append(transition_clips[2])  # Add current clip
                    else:
                        # Fallback: just add current clip
                        transitioned_clips.append(current_clip)
                
                # Concatenate all transitioned clips
                final_video = concatenate_videoclips(transitioned_clips, method="chain")
            else:
                # Single clip, no transitions needed
                final_video = concatenate_videoclips(video_clips, method="chain")
            
            # Set final output path
            final_output = os.path.join(self.output_dir, output_filename)
            
            # Write final video
            final_video.write_videofile(
                final_output,
                fps=24,
                audio_codec='aac',
                codec='libx264',
                logger=None
            )
            
            # Clean up
            for clip in video_clips:
                clip.close()
            final_video.close()
            
            # Remove individual scene files and downloaded videos
            for scene_path in scene_clips:
                if os.path.exists(scene_path):
                    os.remove(scene_path)
            
            # Clean up downloaded videos
            self._cleanup_downloaded_videos(len(scenes_data))
            
            return {
                "success": True,
                "final_video": final_output,
                "total_duration": total_duration,
                "total_scenes": len(scenes_data),
                "transitions_used": getattr(self, '_transitions_log', []),
                "message": f"Final video compiled successfully with dynamic transitions: {final_output}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to compile final video"
            }
    
    def add_intro_outro(self, video_path: str, intro_text: str = None, outro_text: str = None) -> dict:
        """
        Add intro and outro to the video
        
        Args:
            video_path (str): Path to the main video
            intro_text (str): Text for intro screen
            outro_text (str): Text for outro screen
            
        Returns:
            dict: Result with enhanced video path
        """
        try:
            main_video = VideoFileClip(video_path)
            clips = []
            
            # Create intro if provided
            if intro_text:
                intro_clip = ColorClip(size=(1920, 1080), color=(10, 10, 30), duration=3)
                intro_text_clip = TextClip(
                    text=intro_text,
                    font_size=80,
                    color='white'
                ).with_position('center').with_duration(3)
                
                intro_final = CompositeVideoClip([intro_clip, intro_text_clip])
                clips.append(intro_final)
            
            # Add main video
            clips.append(main_video)
            
            # Create outro if provided
            if outro_text:
                outro_clip = ColorClip(size=(1920, 1080), color=(30, 10, 10), duration=3)
                outro_text_clip = TextClip(
                    text=outro_text,
                    font_size=60,
                    color='white'
                ).with_position('center').with_duration(3)
                
                outro_final = CompositeVideoClip([outro_clip, outro_text_clip])
                clips.append(outro_final)
            
            # Concatenate all clips
            final_video = concatenate_videoclips(clips, method="chain")
            
            # Create output path
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            enhanced_output = os.path.join(self.output_dir, f"{base_name}_enhanced.mp4")
            
            # Write enhanced video
            final_video.write_videofile(
                enhanced_output,
                fps=24,
                audio_codec='aac',
                codec='libx264',
                logger=None
            )
            
            # Clean up
            for clip in clips:
                clip.close()
            final_video.close()
            
            return {
                "success": True,
                "enhanced_video": enhanced_output,
                "message": "Intro/outro added successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add intro/outro"
            }
    
    def _cleanup_downloaded_videos(self, num_scenes: int) -> None:
        """
        Clean up downloaded video files after compilation
        
        Args:
            num_scenes (int): Number of scenes to clean up
        """
        try:
            videos_dir = os.path.join("static", "videos")
            if os.path.exists(videos_dir):
                for i in range(num_scenes):
                    downloaded_video = os.path.join(videos_dir, f"downloaded_{i}.mp4")
                    if os.path.exists(downloaded_video):
                        os.remove(downloaded_video)
                        print(f"🗑️  Cleaned up: {downloaded_video}")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up downloaded videos: {e}")
    
    def get_video_cache_info(self) -> dict:
        """
        Get information about cached/downloaded videos
        
        Returns:
            dict: Information about video cache
        """
        try:
            videos_dir = os.path.join("static", "videos")
            if not os.path.exists(videos_dir):
                return {
                    "cache_exists": False,
                    "cached_videos": 0,
                    "total_size_mb": 0
                }
            
            cached_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
            total_size = sum(os.path.getsize(os.path.join(videos_dir, f)) for f in cached_files)
            total_size_mb = total_size / (1024 * 1024)
            
            return {
                "cache_exists": True,
                "cached_videos": len(cached_files),
                "cached_files": cached_files,
                "total_size_mb": total_size_mb,
                "cache_directory": videos_dir
            }
            
        except Exception as e:
            return {
                "cache_exists": False,
                "error": str(e),
                "message": "Failed to get cache info"
            }