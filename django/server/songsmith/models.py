from django.db import models

# Create your models here.
# songsmith/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_refresh_token = models.TextField(null=True, blank=True)
    last_sync = models.DateTimeField(null=True)

    def __str__(self):
        return self.user.username

class ListeningContext(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    context_type = models.CharField(max_length=50)
    context_value = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.context_type}: {self.context_value}"

class SongHistory(models.Model):
    context = models.ForeignKey(ListeningContext, on_delete=models.CASCADE)
    spotify_track_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
    liked = models.BooleanField(null=True)

    class Meta:
        ordering = ['-played_at']