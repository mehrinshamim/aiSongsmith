from django.shortcuts import render

'''
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to the API. Visit /api/ for endpoints."})
'''
# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def recommendations(self, request):
        sp = self.get_spotify_client(request.user)
        context = request.data.get('context', {})
        
        # Get user's top tracks and artists
        top_tracks = sp.current_user_top_tracks(limit=5)
        top_artists = sp.current_user_top_artists(limit=3)
        
        # Get recommendations based on user's taste
        seed_tracks = [track['id'] for track in top_tracks['items']]
        seed_artists = [artist['id'] for artist in top_artists['items']]
        
        recommendations = sp.recommendations(
            seed_tracks=seed_tracks[:2],
            seed_artists=seed_artists[:1],
            limit=10
        )
        
        return Response(recommendations)

    @action(detail=False, methods=['post'])
    def play(self, request):
        track_id = request.data.get('track_id')
        context_id = request.data.get('context_id')
        
        # Log the play in history
        SongHistory.objects.create(
            user=request.user,
            spotify_track_id=track_id,
            context_id=context_id
        )
        
        return Response({'status': 'success'})

    def get_spotify_client(self, user):
        profile = Profile.objects.get(user=user)
        auth_manager = SpotifyOAuth(
            client_id='your_client_id',
            client_secret='your_client_secret',
            redirect_uri='your_redirect_uri',
            scope='user-top-read user-modify-playback-state'
        )
        return spotipy.Spotify(auth_manager=auth_manager)
