#songsmith/admin.py
from django.contrib import admin
from .models import Profile, ListeningContext, SongDetail, PlayHistory

# Register your models here.
admin.site.register(Profile)
admin.site.register(ListeningContext)
admin.site.register(SongDetail)
admin.site.register(PlayHistory)
