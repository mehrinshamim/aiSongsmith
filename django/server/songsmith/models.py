# backend/songsmith/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

#Create your models here
class Profile(models.Model):
    #user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    spotify_refresh_token = models.TextField(null=True)
    spotify_access_token = models.TextField(null=True)
    token_expires_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ListeningContext(models.Model):
    context_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    context = models.CharField(max_length=50)  # e.g., 'happy', 'workout', 'focused'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}'s {self.context} session"

class SongDetail(models.Model):
    song_id = models.CharField(max_length=100, primary_key=True)  # Spotify track ID
    name = models.CharField(max_length=200)
    artists = models.JSONField()  # Store as JSON array
    lyrics = models.TextField(null=True)
    lyrics_last_updated = models.DateTimeField(null=True)
    
    def __str__(self):
        return f"{self.name} by {', '.join(self.artists)}"

class PlayHistory(models.Model):
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context = models.ForeignKey(ListeningContext, on_delete=models.CASCADE)
    song = models.ForeignKey(SongDetail, on_delete=models.CASCADE)
    liked = models.BooleanField(null=True)
    order_in_list = models.IntegerField()
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-played_at']
        
    def __str__(self):
        return f"{self.song.name} - {self.context.context}"
