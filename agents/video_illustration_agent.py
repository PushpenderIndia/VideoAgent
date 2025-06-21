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
        self.__dict__['model'] = genai.GenerativeModel('gemini-pro')
        self.__dict__['scraper'] = cloudscraper.create_scraper()
    
    def generate_search_keywords(self, dialogue: str) -> dict:
        """
        Generate search keywords for video illustrations based on dialogue content
        
        Args:
            dialogue (str): The dialogue/content to generate keywords for
            
        Returns:
            dict: Keywords in JSON format
        """
        prompt = f'''Give me the search keyword for finding the vector illustrations for this content and I want the output in json format, strictly like this {{"keywords": ["keyword1", "keyword2"]}}: {dialogue}'''
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            
            keywords_text = response.text
            
            # Extract JSON from the response
            start_idx = keywords_text.find('{')
            end_idx = keywords_text.rfind('}') + 1
            json_str = keywords_text[start_idx:end_idx]
            
            keywords_data = json.loads(json_str)
            
            return {
                "success": True,
                "keywords": keywords_data["keywords"],
                "dialogue": dialogue,
                "message": "Keywords generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "dialogue": dialogue,
                "message": "Failed to generate keywords"
            }
    
    def search_getty_videos(self, keywords: list) -> dict:
        """
        Search for videos on Getty Images using keywords
        
        Args:
            keywords (list): List of search keywords
            
        Returns:
            dict: Video URLs and poster images
        """
        results = []
        
        for keyword in keywords:
            try:
                # Format the search term for Getty Images
                search_term = keyword.lower().strip().replace(" ", "-").replace(".", "")
                url = f'https://www.gettyimages.in/videos/{search_term}?assettype=film&excludenudity=false&agreements=&phrase={keyword.replace(" ", "%20")}&sort=mostpopular'
                
                html = self.scraper.get(url).text
                
                # Extract video preview URL
                if '"filmPreviewUrl":"' in html:
                    link = html.split('"filmPreviewUrl":"')[1].split('"')[0].replace("\\u0026", "&")
                    
                    # Generate poster image URL
                    link_part = link.split(".mp4")[0] + ".jpg"
                    if link_part in html:
                        poster_img = link_part + html.split(link_part)[1].split('"')[0].replace("\\u0026", "&")
                    else:
                        poster_img = ""
                    
                    results.append({
                        "keyword": keyword,
                        "video_url": link,
                        "poster_url": poster_img,
                        "success": True
                    })
                else:
                    results.append({
                        "keyword": keyword,
                        "video_url": "",
                        "poster_url": "",
                        "success": False,
                        "error": "No video found"
                    })
                    
            except Exception as e:
                results.append({
                    "keyword": keyword,
                    "video_url": "",
                    "poster_url": "",
                    "success": False,
                    "error": str(e)
                })
        
        successful_results = [r for r in results if r["success"]]
        
        return {
            "success": len(successful_results) > 0,
            "results": results,
            "best_result": successful_results[0] if successful_results else None,
            "total_found": len(successful_results),
            "message": f"Found {len(successful_results)}/{len(keywords)} videos"
        }
    
    def find_illustration_for_dialogue(self, dialogue: str) -> dict:
        """
        Complete workflow: generate keywords and find video illustrations for dialogue
        
        Args:
            dialogue (str): The dialogue content to find illustrations for
            
        Returns:
            dict: Complete result with keywords and video URLs
        """
        # Generate keywords
        keywords_result = self.generate_search_keywords(dialogue)
        
        if not keywords_result["success"]:
            return keywords_result
        
        # Search for videos using the keywords
        video_result = self.search_getty_videos(keywords_result["keywords"])
        
        return {
            "success": video_result["success"],
            "dialogue": dialogue,
            "keywords": keywords_result["keywords"],
            "video_results": video_result["results"],
            "best_video": video_result["best_result"],
            "message": f"Found illustration for dialogue: {dialogue[:50]}..."
        } 