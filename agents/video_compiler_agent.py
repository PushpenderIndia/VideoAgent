from google.adk.agents import LlmAgent
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
import os
import json
import requests
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
    
    def create_scene_video(self, scene_data: dict, scene_index: int) -> dict:
        """
        Create a video clip for a single scene
        
        Args:
            scene_data (dict): Scene data with audio, video/illustration files
            scene_index (int): Index of the scene
            
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
                if video_clip.duration < audio_duration:
                    video_clip = video_clip.looped(duration=audio_duration)
                else:
                    video_clip = video_clip.subclipped(0, audio_duration)
                    
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
                        if video_clip.duration < audio_duration:
                            video_clip = video_clip.looped(duration=audio_duration)
                        else:
                            video_clip = video_clip.subclipped(0, audio_duration)
                        
                        # Resize to standard dimensions if needed
                        if video_clip.size != (1920, 1080):
                            video_clip = video_clip.resized((1920, 1080))
                        
                        print(f"✅ Using downloaded video: {download_result['message']}")
                        
                    except Exception as e:
                        print(f"⚠️  Error processing downloaded video: {e}")
                        # Fallback to colored background with title
                        video_clip = ColorClip(size=(1920, 1080), color=(0, 50, 100), duration=audio_duration)
                        
                        title_text = TextClip(
                            text=scene_data.get("title", f"Scene {scene_index + 1}"),
                            font_size=60,
                            color='white'
                        ).with_position('center').with_duration(audio_duration)
                        
                        video_clip = CompositeVideoClip([video_clip, title_text])
                else:
                    print(f"⚠️  Video download failed: {download_result['message']}")
                    # Fallback to colored background with title
                    video_clip = ColorClip(size=(1920, 1080), color=(0, 50, 100), duration=audio_duration)
                    
                    title_text = TextClip(
                        text=scene_data.get("title", f"Scene {scene_index + 1}"),
                        font_size=60,
                        color='white'
                    ).with_position('center').with_duration(audio_duration)
                    
                    video_clip = CompositeVideoClip([video_clip, title_text])
                
            else:
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
    
    def compile_final_video(self, scenes_data: list, output_filename: str = "final_video.mp4") -> dict:
        """
        Compile all scene videos into final video
        
        Args:
            scenes_data (list): List of scene data dictionaries
            output_filename (str): Name of the final output video
            
        Returns:
            dict: Result with final video path
        """
        try:
            scene_clips = []
            total_duration = 0
            
            # Create individual scene videos
            for i, scene_data in enumerate(scenes_data):
                scene_result = self.create_scene_video(scene_data, i)
                
                if scene_result["success"]:
                    scene_clips.append(scene_result["scene_video"])
                    total_duration += scene_result["duration"]
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create scene {i}: {scene_result['error']}",
                        "message": "Scene creation failed"
                    }
            
            # Load all scene video clips
            video_clips = []
            for scene_path in scene_clips:
                clip = VideoFileClip(scene_path)
                video_clips.append(clip)
            
            # Concatenate all clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
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
                "message": f"Final video compiled successfully: {final_output}"
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
            final_video = concatenate_videoclips(clips, method="compose")
            
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