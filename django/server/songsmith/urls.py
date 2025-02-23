from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpotifyViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'spotify', SpotifyViewSet, basename='spotify')

urlpatterns = [
   # path('', home, name='home'),  # Add the home view
    path('', include(router.urls)),  # Remove 'api/' prefix here
]