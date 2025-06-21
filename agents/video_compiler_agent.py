from google.adk.agents import LlmAgent
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
import os
import json
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
                    video_clip = video_clip.loop(duration=audio_duration)
                else:
                    video_clip = video_clip.subclip(0, audio_duration)
                    
            elif scene_data.get("video_url"):
                # Use downloaded Getty Images video
                # Note: You'll need to implement video downloading from URLs
                # For now, we'll create a text overlay on colored background
                video_clip = ColorClip(size=(1920, 1080), color=(0, 50, 100), duration=audio_duration)
                
                # Add title text
                title_text = TextClip(
                    scene_data.get("title", f"Scene {scene_index + 1}"),
                    fontsize=60,
                    color='white',
                    font='Arial-Bold'
                ).set_position('center').set_duration(audio_duration)
                
                video_clip = CompositeVideoClip([video_clip, title_text])
                
            else:
                # Create a simple background with text
                video_clip = ColorClip(size=(1920, 1080), color=(20, 20, 50), duration=audio_duration)
                
                # Add scene content as text overlay
                content_text = "\n".join(scene_data.get("content", ["No content"]))
                if len(content_text) > 200:
                    content_text = content_text[:200] + "..."
                
                text_clip = TextClip(
                    content_text,
                    fontsize=40,
                    color='white',
                    font='Arial',
                    size=(1600, None),
                    method='caption'
                ).set_position('center').set_duration(audio_duration)
                
                video_clip = CompositeVideoClip([video_clip, text_clip])
            
            # Set audio
            final_clip = video_clip.set_audio(audio_clip)
            
            # Save scene video
            scene_output = os.path.join(self.output_dir, f"scene_{scene_index:02d}.mp4")
            final_clip.write_videofile(
                scene_output,
                fps=24,
                audio_codec='aac',
                codec='libx264',
                verbose=False,
                logger=None,
                temp_audiofile_path=f"temp_audio_{scene_index}.m4a"
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
    
    def download_video_from_url(self, video_url: str, output_path: str) -> dict:
        """
        Download video from URL (Getty Images)
        
        Args:
            video_url (str): URL of the video to download
            output_path (str): Path to save the downloaded video
            
        Returns:
            dict: Result of download operation
        """
        try:
            import requests
            
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return {
                "success": True,
                "file_path": output_path,
                "message": "Video downloaded successfully"
            }
            
        except Exception as e:
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
                verbose=False,
                logger=None
            )
            
            # Clean up
            for clip in video_clips:
                clip.close()
            final_video.close()
            
            # Remove individual scene files
            for scene_path in scene_clips:
                if os.path.exists(scene_path):
                    os.remove(scene_path)
            
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
                    intro_text,
                    fontsize=80,
                    color='white',
                    font='Arial-Bold'
                ).set_position('center').set_duration(3)
                
                intro_final = CompositeVideoClip([intro_clip, intro_text_clip])
                clips.append(intro_final)
            
            # Add main video
            clips.append(main_video)
            
            # Create outro if provided
            if outro_text:
                outro_clip = ColorClip(size=(1920, 1080), color=(30, 10, 10), duration=3)
                outro_text_clip = TextClip(
                    outro_text,
                    fontsize=60,
                    color='white',
                    font='Arial-Bold'
                ).set_position('center').set_duration(3)
                
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
                verbose=False,
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