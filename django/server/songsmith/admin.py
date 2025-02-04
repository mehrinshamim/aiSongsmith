#songsmith/admin.py
from django.contrib import admin
from .models import Profile, ListeningContext, SongHistory

# Register your models here.
admin.site.register(Profile)
admin.site.register(ListeningContext)
admin.site.register(SongHistory)