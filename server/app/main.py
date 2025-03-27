from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn
from .routers import spotify #,genius

# Load environment variables
load_dotenv()

app = FastAPI(title="Spotify AI Songsmith API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5713")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(spotify.router)
#app.include_router(genius.router , prefix="/genius", tags=["genius"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Spotify AI Songsmith API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)