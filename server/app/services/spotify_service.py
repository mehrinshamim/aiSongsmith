from fastapi import HTTPException
import httpx
import base64
import os
from typing import Dict, Any
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Spotify API configuration
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:8000/spotify/callback")
API_BASE_URL = "https://api.spotify.com/v1"

async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token"""
    
    # Exchange the authorization code for an access token
    token_url = "https://accounts.spotify.com/api/token"
    
    # Prepare the authorization header
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    # Prepare the request body
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    # Make the token request
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve access token")
        return response.json()

async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh an expired access token"""
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to refresh access token")
        return response.json()

async def get_spotify_data(endpoint: str, access_token: str) -> Dict[str, Any]:
    """Helper function to fetch data from Spotify API"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch data from {endpoint}")
        return response.json()

async def get_music_taste_data(access_token: str) -> Dict[str, Any]:
    """Get comprehensive music taste data for the user"""
    tasks = [
        get_spotify_data("/me/top/artists?time_range=short_term&limit=10", access_token),
        get_spotify_data("/me/top/artists?time_range=medium_term&limit=10", access_token),
        get_spotify_data("/me/top/artists?time_range=long_term&limit=10", access_token),
        get_spotify_data("/me/top/tracks?time_range=short_term&limit=10", access_token),
        get_spotify_data("/me/top/tracks?time_range=medium_term&limit=10", access_token),
        get_spotify_data("/me/top/tracks?time_range=long_term&limit=10", access_token),
        get_spotify_data("/me/player/recently-played?limit=20", access_token),
        get_spotify_data("/me/playlists?limit=20", access_token),
        get_spotify_data("/me/tracks?limit=20", access_token),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "top_artists": {
            "short_term": results[0]["items"],
            "medium_term": results[1]["items"],
            "long_term": results[2]["items"],
        },
        "top_tracks": {
            "short_term": results[3]["items"],
            "medium_term": results[4]["items"],
            "long_term": results[5]["items"],
        },
        "recently_played": results[6]["items"],
        "playlists": results[7]["items"],
        "saved_tracks": results[8]["items"],
    }
