// components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  // Use import.meta.env instead of process.env
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  return (
    <div className="home-container">
      <h1>AI Songsmith</h1>
      <p>Generate AI music recommendations based on your Spotify listening history</p>
      
      <div className="auth-section">
        <h2>Get Started</h2>
        <p>Connect your Spotify account to analyze your music taste</p>
        <a 
          href={`${apiUrl}/login`} 
          className="spotify-button"
        >
          Connect with Spotify
        </a>
      </div>
    </div>
  );
}

export default Home;
