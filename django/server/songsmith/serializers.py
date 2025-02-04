
# backend/songsmith/serializers.py
from rest_framework import serializers
from .models import Profile, ListeningContext, SongDetail, PlayHistory

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['spotify_refresh_token', 'spotify_access_token']

class SongDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongDetail
        fields = ['song_id', 'name', 'artists']

class PlayHistorySerializer(serializers.ModelSerializer):
    song = SongDetailSerializer()
    
    class Meta:
        model = PlayHistory
        fields = ['history_id', 'song', 'liked', 'played_at', 'context']