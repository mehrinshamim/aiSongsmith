from typing import Optional, Dict, Any
import httpx
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GeniusAPIClient:
    def __init__(self):
        """Initialize Genius API client with error checking"""
        self.base_url = "https://api.genius.com"
        
        self.access_token = os.getenv("GENIUS_ACCESS_TOKEN")
        if not self.access_token:
            logger.error("Genius API access token is missing!")
            raise ValueError("GENIUS_ACCESS_TOKEN environment variable is not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def search_song(self, track_name: str, artist_name: str) -> Optional[Dict[str, Any]]:
        """Search for a song on Genius API"""
        if not track_name or not artist_name:
            logger.warning("Empty track or artist name provided")
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "q": f"{track_name} {artist_name}",
                    "type": "song"
                }
                response = await client.get(
                    f"{self.base_url}/search", 
                    params=params, 
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                hits = data.get('response', {}).get('hits', [])
                
                for hit in hits:
                    song = hit.get('result', {})
                    song_title = song.get('title', '').lower()
                    song_artist = song.get('primary_artist', {}).get('name', '').lower()
                    
                    if (track_name.lower() in song_title or song_title in track_name.lower()) and \
                       (artist_name.lower() in song_artist or song_artist in artist_name.lower()):
                        return song
                
                logger.info(f"No exact match found for {track_name} by {artist_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error in song search: {e}")
            return None

    async def get_song_details(self, track_name: str, artist_name: str) -> Optional[Dict[str, Any]]:
        """Fetch song details"""
        try:
            song = await self.search_song(track_name, artist_name)
            
            if not song:
                return None
            
            return {
                "title": song.get('title', 'Unknown Title'),
                "artist": song.get('primary_artist', {}).get('name', 'Unknown Artist'),
                "song_art_image_url": song.get('song_art_image_url', ''),
                "genius_url": song.get('url', ''),
                "summary": "Note: Detailed summary requires additional web scraping implementation",
                "lyrics": "Lyrics access limited due to copyright restrictions"
            }
        
        except Exception as e:
            logger.error(f"Error fetching song details: {e}")
            return None

    async def check_health(self) -> Dict[str, Any]:
        """Check Genius API health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={"q": "test"},
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "Successfully connected to Genius API",
                        "api_version": "v1",
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "status": "degraded",
                        "message": f"Genius API returned non-200 status: {response.status_code}",
                        "details": response.json()
                    }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise