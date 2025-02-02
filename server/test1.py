import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from textblob import TextBlob
import lyricsgenius
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MoodBasedRecommender:
    def __init__(self, spotify_client_id, spotify_client_secret, genius_token):
        # Initialize Spotify API client
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret
        ))
        # Initialize Genius API client for lyrics
        self.genius = lyricsgenius.Genius(genius_token)
        
        # Define emotion categories and their associated musical features
        self.emotion_profiles = {
            'angry': {
                'tempo': (120, 200),
                'energy': (0.7, 1.0),
                'valence': (0.0, 0.4),
                'keywords': ['hate', 'anger', 'rage', 'fight', 'betrayal'],
                'genres': ['metal', 'rock', 'punk']
            },
            'sad': {
                'tempo': (60, 100),
                'energy': (0.0, 0.4),
                'valence': (0.0, 0.3),
                'keywords': ['lonely', 'hurt', 'pain', 'cry', 'heartbreak'],
                'genres': ['blues', 'indie', 'soul']
            },
            'happy': {
                'tempo': (100, 160),
                'energy': (0.6, 1.0),
                'valence': (0.7, 1.0),
                'keywords': ['love', 'happy', 'joy', 'dance', 'smile'],
                'genres': ['pop', 'dance', 'disco']
            },
            'peaceful': {
                'tempo': (40, 100),
                'energy': (0.0, 0.3),
                'valence': (0.3, 0.7),
                'keywords': ['calm', 'peace', 'quiet', 'gentle', 'soft'],
                'genres': ['ambient', 'classical', 'acoustic']
            }
        }
        
    def analyze_user_library(self, username):
        """Analyze user's Spotify library to understand their music preferences"""
        playlists = self.sp.user_playlists(username)
        tracks_data = []
        
        for playlist in playlists['items']:
            results = self.sp.playlist_tracks(playlist['id'])
            for item in results['items']:
                if item['track']:
                    track = item['track']
                    audio_features = self.sp.audio_features(track['id'])[0]
                    if audio_features:
                        tracks_data.append({
                            'id': track['id'],
                            'name': track['name'],
                            'artist': track['artists'][0]['name'],
                            'tempo': audio_features['tempo'],
                            'energy': audio_features['energy'],
                            'valence': audio_features['valence'],
                            'genre': self.get_artist_genres(track['artists'][0]['id'])
                        })
        
        return pd.DataFrame(tracks_data)
    
    def get_artist_genres(self, artist_id):
        """Get primary genre for an artist"""
        try:
            artist = self.sp.artist(artist_id)
            return artist['genres'][0] if artist['genres'] else 'unknown'
        except:
            return 'unknown'
    
    def analyze_mood_from_text(self, text):
        """Analyze user's input text to determine emotional state"""
        analysis = TextBlob(text)
        
        # Get polarity (-1 to 1) and subjectivity (0 to 1)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        
        # Basic emotion classification based on polarity and words
        if polarity < -0.5:
            return 'angry' if 'hate' in text.lower() or 'angry' in text.lower() else 'sad'
        elif polarity < 0:
            return 'sad'
        elif polarity > 0.5:
            return 'happy'
        else:
            return 'peaceful'
    
    def get_song_lyrics(self, song_name, artist_name):
        """Fetch and analyze lyrics for a song"""
        try:
            song = self.genius.search_song(song_name, artist_name)
            return song.lyrics if song else ""
        except:
            return ""
    
    def analyze_lyrics_sentiment(self, lyrics):
        """Analyze the emotional content of lyrics"""
        if not lyrics:
            return None
        
        analysis = TextBlob(lyrics)
        return {
            'polarity': analysis.sentiment.polarity,
            'subjectivity': analysis.sentiment.subjectivity
        }
    
    def recommend_songs(self, user_text, user_library_df, n_recommendations=5):
        """Recommend songs based on user's emotional state and situation"""
        # Determine user's current mood
        current_mood = self.analyze_mood_from_text(user_text)
        mood_profile = self.emotion_profiles[current_mood]
        
        # Filter songs by musical features matching the mood
        filtered_df = user_library_df[
            (user_library_df['tempo'].between(*mood_profile['tempo'])) &
            (user_library_df['energy'].between(*mood_profile['energy'])) &
            (user_library_df['valence'].between(*mood_profile['valence']))
        ]
        
        # Score each song based on genre match and lyrical content
        scored_songs = []
        for _, song in filtered_df.iterrows():
            lyrics = self.get_song_lyrics(song['name'], song['artist'])
            lyric_sentiment = self.analyze_lyrics_sentiment(lyrics)
            
            # Calculate overall score
            genre_score = 1 if song['genre'] in mood_profile['genres'] else 0
            lyric_score = 0
            if lyric_sentiment:
                # Adjust scoring based on mood
                if current_mood in ['angry', 'sad']:
                    lyric_score = (1 - lyric_sentiment['polarity']) * 0.5
                else:
                    lyric_score = (1 + lyric_sentiment['polarity']) * 0.5
            
            total_score = genre_score * 0.4 + lyric_score * 0.6
            
            scored_songs.append({
                'name': song['name'],
                'artist': song['artist'],
                'score': total_score
            })
        
        # Sort by score and return top recommendations
        scored_songs.sort(key=lambda x: x['score'], reverse=True)
        return scored_songs[:n_recommendations]

    def get_situation_specific_recommendations(self, situation, user_library_df):
        """Get recommendations for specific situations like breakups"""
        situation_keywords = {
            'breakup': {
                'positive': ['strong', 'independent', 'better', 'free', 'over'],
                'negative': ['betrayal', 'cheating', 'heartbreak', 'revenge', 'goodbye']
            },
            # Add more situations as needed
        }
        
        recommendations = []
        for _, song in user_library_df.iterrows():
            lyrics = self.get_song_lyrics(song['name'], song['artist'])
            if lyrics:
                # Check for situation-specific keywords in lyrics
                keyword_matches = sum(1 for keyword in situation_keywords[situation]['negative'] 
                                   if keyword in lyrics.lower())
                if keyword_matches > 0:
                    recommendations.append({
                        'name': song['name'],
                        'artist': song['artist'],
                        'relevance': keyword_matches
                    })
        
        return sorted(recommendations, key=lambda x: x['relevance'], reverse=True)[:5]