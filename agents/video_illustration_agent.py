from google.adk.agents import LlmAgent
import google.generativeai as genai
import cloudscraper
import json
import os
from dotenv import load_dotenv

load_dotenv()

class VideoIllustrationAgent(LlmAgent):
    def __init__(self, gemini_api_key=None):
        super().__init__(
            name="VideoIllustrationAgent",
            description="Finds video illustrations from Getty Images based on content keywords"
        )
        self._initialize_config(gemini_api_key)
    
    def _initialize_config(self, gemini_api_key):
        """Initialize configuration after parent initialization"""
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.__dict__['model'] = genai.GenerativeModel('gemini-2.0-flash')
        self.__dict__['scraper'] = cloudscraper.create_scraper()
        # Track used videos to ensure uniqueness across scenes
        self.__dict__['used_videos'] = set()
    
    def generate_search_keywords(self, dialogue: str, scene_title: str = "", scene_index: int = 0) -> dict:
        """
        Generate search keywords for video illustrations based on scene title and dialogue content
        
        Args:
            dialogue (str): The dialogue/content to generate keywords for
            scene_title (str): The title of the scene (70% priority)
            scene_index (int): Index of the scene for context
            
        Returns:
            dict: Keywords in JSON format with max 3 keywords
        """
        # Create weighted prompt that prioritizes title over dialogue
        if scene_title.strip():
            prompt = f'''Generate exactly 1 search keyword for finding video illustrations. 
            Give 70% priority to the TITLE and 30% priority to the dialogue content.
            Make the keyword specific and unique for scene {scene_index}.
            
            TITLE (70% priority): {scene_title}
            DIALOGUE (30% priority): {dialogue}
            
            Output in JSON format: {{"keyword": "single_keyword"}}
            
            Focus mainly on the title concept, supplemented by dialogue context.'''
        else:
            prompt = f'''Generate exactly 1 search keyword for finding video illustrations based on this content.
            Make the keyword specific and unique for scene {scene_index}.
            
            Content: {dialogue}
            
            Output in JSON format: {{"keyword": "single_keyword"}}'''
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,  # Slightly higher for more variety
                    max_output_tokens=1000
                )
            )
            
            keywords_text = response.text
            
            # Extract JSON from the response
            start_idx = keywords_text.find('{')
            end_idx = keywords_text.rfind('}') + 1
            json_str = keywords_text[start_idx:end_idx]
            
            keywords_data = json.loads(json_str)
            
            # Get single keyword
            keyword = keywords_data.get("keyword", "").strip()
            
            return {
                "success": True,
                "keyword": keyword,
                "dialogue": dialogue,
                "scene_title": scene_title,
                "scene_index": scene_index,
                "message": f"Generated keyword '{keyword}' with title priority"
            }
            
        except Exception as e:
            # Fallback to simple keyword extraction
            if scene_title.strip():
                # Prioritize title for fallback - use first meaningful word from title
                title_words = [word for word in scene_title.lower().split() if len(word) > 2]
                fallback_keyword = title_words[0] if title_words else scene_title.lower().split()[0]
            else:
                # Use first meaningful word from dialogue
                dialogue_words = [word for word in dialogue.lower().split() if len(word) > 2]
                fallback_keyword = dialogue_words[0] if dialogue_words else dialogue.lower().split()[0]
            
            return {
                "success": True,
                "keyword": fallback_keyword,
                "dialogue": dialogue,
                "scene_title": scene_title,
                "scene_index": scene_index,
                "error": str(e),
                "message": f"Used fallback keyword '{fallback_keyword}' with title priority"
            }
    
    def search_getty_videos(self, keywords: list, max_results_per_keyword: int = 3) -> dict:
        """
        Search for multiple videos on Getty Images using keywords
        
        Args:
            keywords (list): List of search keywords
            max_results_per_keyword (int): Maximum results to extract per keyword
            
        Returns:
            dict: Multiple video URLs and poster images
        """
        all_results = []
        
        for keyword in keywords:
            try:
                # Format the search term for Getty Images
                search_term = keyword.lower().strip().replace(" ", "-").replace(".", "")
                url = f'https://www.gettyimages.in/videos/{search_term}?assettype=film&excludenudity=false&agreements=&phrase={keyword.replace(" ", "%20")}&sort=mostpopular'
                
                html = self.scraper.get(url).text
                
                # Extract multiple video preview URLs
                video_urls = []
                poster_urls = []
                
                # Look for all instances of filmPreviewUrl in the HTML
                parts = html.split('"filmPreviewUrl":"')
                for i in range(1, min(len(parts), max_results_per_keyword + 1)):  # Skip first part, limit results
                    try:
                        video_url = parts[i].split('"')[0].replace("\\u0026", "&")
                        
                        # Generate poster image URL
                        poster_base = video_url.split(".mp4")[0] + ".jpg"
                        if poster_base in html:
                            poster_url = poster_base + html.split(poster_base)[1].split('"')[0].replace("\\u0026", "&")
                        else:
                            poster_url = ""
                        
                        video_urls.append(video_url)
                        poster_urls.append(poster_url)
                        
                    except Exception as e:
                        print(f"Error extracting video {i} for keyword '{keyword}': {e}")
                        continue
                
                # Add results for this keyword
                for j, (video_url, poster_url) in enumerate(zip(video_urls, poster_urls)):
                    all_results.append({
                        "keyword": keyword,
                        "video_url": video_url,
                        "poster_url": poster_url,
                        "rank": j + 1,  # Rank within this keyword
                        "success": True
                    })
                
                if not video_urls:
                    all_results.append({
                        "keyword": keyword,
                        "video_url": "",
                        "poster_url": "",
                        "rank": 0,
                        "success": False,
                        "error": "No video found"
                    })
                    
            except Exception as e:
                all_results.append({
                    "keyword": keyword,
                    "video_url": "",
                    "poster_url": "",
                    "rank": 0,
                    "success": False,
                    "error": str(e)
                })
        
        successful_results = [r for r in all_results if r["success"]]
        
        return {
            "success": len(successful_results) > 0,
            "all_results": all_results,
            "successful_results": successful_results,
            "total_found": len(successful_results),
            "message": f"Found {len(successful_results)} videos across {len(keywords)} keywords"
        }
    
    def get_unique_video_for_scene(self, dialogue: str, scene_index: int, scene_title: str = "") -> dict:
        """
        Get a unique video for a scene, ensuring no duplicates across scenes
        
        Args:
            dialogue (str): The dialogue content to find illustrations for
            scene_index (int): Index of the current scene
            scene_title (str): The title of the scene (70% priority)
            
        Returns:
            dict: Result with unique video URL for this scene
        """
        # Generate keywords with scene context and title priority
        keywords_result = self.generate_search_keywords(dialogue, scene_title, scene_index)
        
        if not keywords_result["success"]:
            return keywords_result
        
        # Use the generated single keyword
        keyword = keywords_result.get("keyword", "").strip()
        if not keyword:
            return {
                "success": False,
                "dialogue": dialogue,
                "scene_title": scene_title,
                "scene_index": scene_index,
                "error": "No keyword generated",
                "message": f"Could not generate keyword for scene {scene_index}"
            }
                
        video_result = self.search_getty_videos([keyword], max_results_per_keyword=5)
        
        if video_result["success"]:
            # Find a video that hasn't been used yet
            for video in video_result["successful_results"]:
                video_url = video["video_url"]
                if video_url and video_url not in self.used_videos:
                    # Mark this video as used
                    self.used_videos.add(video_url)
                    
                    return {
                        "success": True,
                        "dialogue": dialogue,
                        "scene_title": scene_title,
                        "scene_index": scene_index,
                        "keyword_used": keyword,
                        "selected_video": video,
                        "video_url": video_url,
                        "poster_url": video["poster_url"],
                        "all_options": len(video_result["successful_results"]),
                        "message": f"Found unique video for scene {scene_index} using keyword '{keyword}'"
                    }
        
        # If no unique video found, return error
        return {
            "success": False,
            "dialogue": dialogue,
            "scene_title": scene_title,
            "scene_index": scene_index,
            "keyword_generated": keyword,
            "error": "No unique video available",
            "used_videos_count": len(self.used_videos),
            "message": f"Could not find unique video for scene {scene_index} with keyword '{keyword}'"
        }
    
    def find_illustration_for_dialogue(self, dialogue: str, scene_index: int = 0, scene_title: str = "") -> dict:
        """
        Complete workflow: generate keywords and find video illustrations for dialogue
        Now with unique video selection per scene and title prioritization
        
        Args:
            dialogue (str): The dialogue content to find illustrations for
            scene_index (int): Index of the scene for uniqueness
            scene_title (str): The title of the scene (70% priority for keywords)
            
        Returns:
            dict: Complete result with keywords and unique video URL
        """
        return self.get_unique_video_for_scene(dialogue, scene_index, scene_title)
    
    def reset_used_videos(self):
        """Reset the used videos tracker for new video generation session"""
        self.used_videos.clear()
    
    def get_used_videos_info(self) -> dict:
        """Get information about currently used videos"""
        return {
            "used_videos_count": len(self.used_videos),
            "used_videos": list(self.used_videos)
        } 