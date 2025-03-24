from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
import os
from dotenv import load_dotenv
import base64
import secrets
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

app = FastAPI(title="Spotify AI Songsmith API")

# CORS middleware to allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spotify API credentials from environment variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/callback")
API_BASE_URL = "https://api.spotify.com/v1"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# We'll store the auth state in memory for simplicity (use Redis or a DB in production)
active_states = {}

# Scopes for Spotify access (permissions)
SCOPES = [
    "user-top-read",
    "user-read-recently-played",
    "user-library-read",
]

# Pydantic models for data validation
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

class UserProfile(BaseModel):
    id: str
    display_name: str
    images: List[Dict[str, Any]] = []

class MusicTaste(BaseModel):
    top_artists: List[Dict[str, Any]]
    top_tracks: List[Dict[str, Any]]
    recently_played: List[Dict[str, Any]]
    playlists: List[Dict[str, Any]]

@app.get("/")
def read_root():
    return {"message": "Welcome to Spotify AI Songsmith API"}

@app.get("/login")
def login():
    """Initiate Spotify OAuth flow"""
    # Generate a random state value for security
    state = secrets.token_urlsafe(16)
    active_states[state] = True
    
    # Construct the authorization URL
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": " ".join(SCOPES),
        "redirect_uri": REDIRECT_URI,
        "state": state
    }
    
    # Build the URL with query parameters
    query_params = "&".join([f"{k}={v}" for k, v in params.items()])
    authorization_url = f"{auth_url}?{query_params}"
    
    # Redirect the user to Spotify's authorization page
    return RedirectResponse(authorization_url)

@app.get("/callback")
async def callback(code: str = None, state: str = None, error: str = None):
    """Handle the Spotify OAuth callback"""
    # Check for errors
    if error:
        raise HTTPException(status_code=400, detail=f"Authorization error: {error}")
    
    # Verify state to prevent CSRF attacks
    if state not in active_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    active_states.pop(state)
    
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
        
        token_data = response.json()
    
    # Redirect to frontend with the token
    redirect_url = f"{FRONTEND_URL}/auth-success?access_token={token_data['access_token']}&refresh_token={token_data['refresh_token']}"
    return RedirectResponse(redirect_url)

@app.get("/refresh-token")
async def refresh_token(refresh_token: str):
    """Refresh an expired access token"""
    token_url = "https://accounts.spotify.com/api/token"
    
    # Prepare the authorization header
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    # Prepare the request body
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    # Make the token request
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to refresh access token")
        
        return response.json()

async def get_spotify_data(endpoint: str, access_token: str):
    """Helper function to fetch data from Spotify API"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch data from {endpoint}")
        
        return response.json()

@app.get("/user-profile")
async def get_user_profile(access_token: str):
    """Get the user's Spotify profile"""
    return await get_spotify_data("/me", access_token)

@app.get("/music-taste")
async def get_music_taste(access_token: str):
    """Get comprehensive music taste data for the user"""
    # Get top artists (short, medium, and long term)
    top_artists_short = await get_spotify_data("/me/top/artists?time_range=short_term&limit=10", access_token)
    top_artists_medium = await get_spotify_data("/me/top/artists?time_range=medium_term&limit=10", access_token)
    top_artists_long = await get_spotify_data("/me/top/artists?time_range=long_term&limit=10", access_token)
    
    # Get top tracks (short, medium, and long term)
    top_tracks_short = await get_spotify_data("/me/top/tracks?time_range=short_term&limit=10", access_token)
    top_tracks_medium = await get_spotify_data("/me/top/tracks?time_range=medium_term&limit=10", access_token)
    top_tracks_long = await get_spotify_data("/me/top/tracks?time_range=long_term&limit=10", access_token)
    
    # Get recently played tracks
    recently_played = await get_spotify_data("/me/player/recently-played?limit=20", access_token)
    
    # Get user's playlists
    playlists = await get_spotify_data("/me/playlists?limit=20", access_token)
    
    # Get user's saved tracks
    saved_tracks = await get_spotify_data("/me/tracks?limit=20", access_token)
    
    # Combine all data into a comprehensive music taste profile
    return {
        "top_artists": {
            "short_term": top_artists_short["items"],
            "medium_term": top_artists_medium["items"],
            "long_term": top_artists_long["items"]
        },
        "top_tracks": {
            "short_term": top_tracks_short["items"],
            "medium_term": top_tracks_medium["items"],
            "long_term": top_tracks_long["items"]
        },
        "recently_played": recently_played["items"],
        "playlists": playlists["items"],
        "saved_tracks": saved_tracks["items"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)