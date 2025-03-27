from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import httpx
import os
from dotenv import load_dotenv
import logging
from ..services.genius_service import GeniusAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")

router = APIRouter(
    prefix="/genius",
    tags=["genius"]
)

@router.get("/song-details", response_model=Dict[str, Any])
async def get_song_details(
    track_name: str = Query(..., min_length=1, description="Name of the track"),
    artist_name: str = Query(..., min_length=1, description="Name of the artist")
):
    """Endpoint to fetch song details from Genius API"""
    if not track_name or not artist_name:
        raise HTTPException(
            status_code=400, 
            detail="Track name and artist name must be provided"
        )

    try:
        genius_client = GeniusAPIClient()
        song_details = await genius_client.get_song_details(track_name, artist_name)
        
        if not song_details:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "not_found",
                    "message": "The requested song could not be found in the Genius database.",
                    "track_name": track_name,
                    "artist_name": artist_name
                }
            )
        
        return song_details
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def check_genius_connection():
    """Health check endpoint to verify Genius API connectivity"""
    try:
        genius_client = GeniusAPIClient()
        return await genius_client.check_health()
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": "Failed to connect to Genius API",
                "error": str(e)
            }
        )
    

#------------------------------
##SCRAPING

#from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup


class LyricsScrapeResponse(BaseModel):
    lyrics_container: str
    title: str
    artist: str
    about: str

@router.post("/scrape-genius/")
async def scrape_genius_page(url: str):
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract lyrics container
        lyrics_container = soup.select_one('div.Lyrics__Container-sc-926d9e10-1')
        #lyrics_text = lyrics_container.get_text(strip=True) if lyrics_container else ""

        # Extract title
        title_elem = soup.select_one('span.SongHeader-desktop__HiddenMask-sc-ffb24f94-11')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"

        # Extract artist
        artist_elem = soup.select_one('.HeaderArtistAndTracklist-desktop__ListArtists-sc-afd25865-1 a')
        artist = artist_elem.get_text(strip=True) if artist_elem else "Unknown Artist"

        # Extract about section
        about_elem = soup.select_one('div.cvMvAz')
        about = about_elem.get_text(strip=True) if about_elem else ""

        return LyricsScrapeResponse(
            lyrics_container=str(lyrics_container),
            title=title,
            artist=artist,
            about=about
        )

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
