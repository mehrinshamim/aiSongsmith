from spotipy.oauth2 import SpotifyOAuth
import spotipy
from config import Config

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=Config.SPOTIFY_CLIENT_ID,
                                               client_secret=Config.SPOTIFY_CLIENT_SECRET,
                                               redirect_uri="https://open.spotify.com/",
                                               scope=["user-library-read", "playlist-read-private"]))

#results = sp.current_user()
#print(results)


