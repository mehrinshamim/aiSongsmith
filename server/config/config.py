# config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    """Base configuration."""
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "default-client-id")  # Default value if not found
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "default-spotify-client-secret")
    SUPABASE_URL = os.getenv("SUPABASE_URL", "default-supabase-url")
    
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Convert string 'True'/'False' to boolean

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Add other development-specific configurations

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Add other production-specific configurations

# Example usage
# To access values, you can do:
# config = Config()
# print(config.SECRET_KEY)
