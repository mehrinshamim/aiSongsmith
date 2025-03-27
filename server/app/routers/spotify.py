from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import secrets
import os
from typing import List, Dict, Any, Optional
from ..services import spotify_service

router = APIRouter(
    prefix="/spotify",
    tags=["spotify"]
)

# Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5713")

# We'll store the auth state in memory for simplicity (use Redis or DB in production)
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
    top_artists: Dict[str, List[Dict[str, Any]]]
    top_tracks: Dict[str, List[Dict[str, Any]]]
    recently_played: List[Dict[str, Any]]
    playlists: List[Dict[str, Any]]
    saved_tracks: List[Dict[str, Any]]

@router.get("/login")
def login():
    """Initiate Spotify OAuth flow"""
    # Generate a random state value for security
    state = secrets.token_urlsafe(16)
    active_states[state] = True
    
    # Construct the authorization URL
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "response_type": "code",
        "client_id": spotify_service.CLIENT_ID,
        "scope": " ".join(SCOPES),
        "redirect_uri": spotify_service.REDIRECT_URI,
        "state": state
    }
    
    # Build the URL with query parameters
    query_params = "&".join([f"{k}={v}" for k, v in params.items()])
    authorization_url = f"{auth_url}?{query_params}"
    
    # Redirect the user to Spotify's authorization page
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def callback(code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """Handle the Spotify OAuth callback"""
    # Check for errors
    if error:
        raise HTTPException(status_code=400, detail=f"Authorization error: {error}")
    
    # Verify state to prevent CSRF attacks
    if not state or state not in active_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    active_states.pop(state)

    # Exchange the authorization code for an access token
    token_data = await spotify_service.exchange_code_for_token(code)
   
    # Redirect to frontend with the token
    redirect_url = f"{FRONTEND_URL}/auth-success?access_token={token_data['access_token']}&refresh_token={token_data['refresh_token']}"
    return RedirectResponse(redirect_url)

@router.get("/refresh-token", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh an expired access token"""
    return await spotify_service.refresh_access_token(refresh_token)

@router.get("/user-profile", response_model=UserProfile)
async def get_user_profile(access_token: str):
    """Get the user's Spotify profile"""
    return await spotify_service.get_spotify_data("/me", access_token)

@router.get("/music-taste", response_model=MusicTaste)
async def get_music_taste(access_token: str):
    """Get comprehensive music taste data for the user"""
    return await spotify_service.get_music_taste_data(access_token)