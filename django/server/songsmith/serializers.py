# songsmith/serializers.py
from rest_framework import serializers
from .models import Profile, ListeningContext, SongHistory

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['spotify_refresh_token', 'last_sync']

class ListeningContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningContext
        fields = ['id', 'context_type', 'context_value', 'created_at']

class SongHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SongHistory
        fields = ['context', 'spotify_track_id', 'played_at', 'liked']