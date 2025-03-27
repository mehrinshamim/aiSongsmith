import React from 'react';

function Home() {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  return (
    <div className="flex min-h-screen items-center justify-center bg-black px-4">
      <div className="w-full max-w-md text-center">
        <h1 className="text-5xl font-bold mb-6 text-green-500">AI Songsmith</h1>
        <p className="text-gray-300 mb-8 text-lg">
          Generate AI music recommendations based on your Spotify listening history
        </p>
        
        <div className="bg-gray-900 rounded-xl p-8 shadow-2xl">
          <h2 className="text-2xl font-semibold mb-4 text-white">Get Started</h2>
          <p className="text-gray-400 mb-6">
            Connect your Spotify account to analyze your music taste
          </p>
          
          <a
            href={`${apiUrl}/spotify/login`}
            className="w-full inline-block bg-green-500 text-black font-bold py-3 px-6 rounded-full 
            hover:bg-green-400 transition-colors duration-300 ease-in-out 
            transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
          >
            Connect with Spotify
          </a>
        </div>
      </div>
    </div>
  );
}

export default Home;