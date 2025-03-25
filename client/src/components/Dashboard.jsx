import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [profile, setProfile] = useState(null);
  const [musicTaste, setMusicTaste] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('medium_term');
  
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  useEffect(() => {
    const accessToken = localStorage.getItem('spotifyAccessToken');
    
    if (!accessToken) {
      navigate('/');
      return;
    }
    
    const fetchUserData = async () => {
      try {
        // Fetch user profile
        const profileRes = await fetch(`${apiUrl}/user-profile?access_token=${accessToken}`);
        
        if (!profileRes.ok) {
          // Handle unauthorized or expired token
          if (profileRes.status === 401) {
            await refreshAccessToken();
            return;
          }
          throw new Error('Failed to fetch user profile');
        }
        
        const profileData = await profileRes.json();
        setProfile(profileData);
        
        // Fetch music taste data
        const musicTasteRes = await fetch(`${apiUrl}/music-taste?access_token=${accessToken}`);
        
        if (!musicTasteRes.ok) {
          throw new Error('Failed to fetch music taste data');
        }
        
        const musicTasteData = await musicTasteRes.json();
        setMusicTaste(musicTasteData);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching user data:', err);
        setError(err.message);
        setLoading(false);
      }
    };
    
    fetchUserData();
  }, [apiUrl, navigate]);
  
  const refreshAccessToken = async () => {
    try {
      const refreshToken = localStorage.getItem('spotifyRefreshToken');
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await fetch(`${apiUrl}/refresh-token?refresh_token=${refreshToken}`);
      
      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }
      
      const data = await response.json();
      localStorage.setItem('spotifyAccessToken', data.access_token);
      
      // Reload the page to retry with new token
      window.location.reload();
    } catch (err) {
      console.error('Error fetching user data:', err);
      setError('Authentication expired. Please login again.');
      localStorage.removeItem('spotifyAccessToken');
      localStorage.removeItem('spotifyRefreshToken');
      
      // Redirect to home after a short delay
      setTimeout(() => navigate('/'), 3000);
    }
  };
  
  const logout = () => {
    localStorage.removeItem('spotifyAccessToken');
    localStorage.removeItem('spotifyRefreshToken');
    navigate('/');
  };
  
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-green-500 mx-auto mb-4"></div>
          <p className="text-xl">Loading your music profile...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-red-500">
        <p className="text-2xl">Error: {error}</p>
      </div>
    );
  }
  
  // Time range selection component
  const TimeRangeTabs = () => (
    <div className="flex space-x-2 mb-4">
      {['short_term', 'medium_term', 'long_term'].map((range) => (
        <button
          key={range}
          onClick={() => setTimeRange(range)}
          className={`px-3 py-1 rounded-full text-sm 
            ${timeRange === range 
              ? 'bg-green-500 text-black' 
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
        >
          {range === 'short_term' ? 'Last Month' : 
           range === 'medium_term' ? 'Last 6 Months' : 
           'All Time'}
        </button>
      ))}
    </div>
  );
  
  return (
    <div className="min-h-screen bg-black text-white p-6 max-w-7xl mx-auto">
      {/* User Profile Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          {profile?.images?.[0] && (
            <img 
              src={profile.images[0].url} 
              alt={profile.display_name} 
              className="w-16 h-16 rounded-full border-2 border-green-500" 
            />
          )}
          <h1 className="text-3xl font-bold">Welcome, {profile?.display_name}</h1>
        </div>
        <button 
          onClick={logout} 
          className="bg-transparent border border-white text-white px-4 py-2 rounded-full hover:bg-white hover:text-black transition-colors"
        >
          Logout
        </button>
      </div>
      
      {/* Navigation Tabs */}
      <div className="flex space-x-2 mb-8 border-b border-gray-800">
        {['overview', 'artists', 'tracks', 'recent', 'playlists'].map(tab => (
          <button
            key={tab}
            className={`px-4 py-2 text-sm uppercase tracking-wider 
              ${activeTab === tab 
                ? 'text-green-500 border-b-2 border-green-500' 
                : 'text-gray-400 hover:text-white'}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>
      
      {/* Dashboard Content */}
      {musicTaste && (
        <div>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid md:grid-cols-4 gap-4">
              {[
                { 
                  title: 'Top Genre', 
                  value: getTopGenre(musicTaste.top_artists.medium_term) 
                },
                { 
                  title: 'Top Artist', 
                  value: musicTaste.top_artists.medium_term[0]?.name || 'None' 
                },
                { 
                  title: 'Top Track', 
                  value: musicTaste.top_tracks.medium_term[0]?.name || 'None' 
                },
                { 
                  title: 'Playlists', 
                  value: musicTaste.playlists.length 
                }
              ].map((stat, index) => (
                <div 
                  key={index} 
                  className="bg-gray-900 rounded-lg p-4 text-center hover:bg-gray-800 transition-colors"
                >
                  <h3 className="text-gray-400 mb-2">{stat.title}</h3>
                  <p className="text-xl font-bold text-green-500">{stat.value}</p>
                </div>
              ))}
            </div>
          )}
          
          {/* Artists Tab */}
          {activeTab === 'artists' && (
            <div>
              <TimeRangeTabs />
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {musicTaste.top_artists[timeRange].map(artist => (
                  <div 
                    key={artist.id} 
                    className="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-800 transition-colors"
                  >
                    {artist.images?.[0] && (
                      <img 
                        src={artist.images[0].url} 
                        alt={artist.name} 
                        className="w-full aspect-square object-cover"
                      />
                    )}
                    <div className="p-3">
                      <h3 className="font-bold text-sm truncate">{artist.name}</h3>
                      <p className="text-xs text-gray-400 truncate">
                        {artist.genres.slice(0, 2).join(', ')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Tracks Tab */}
          {activeTab === 'tracks' && (
            <div>
              <TimeRangeTabs />
              <div className="bg-gray-900 rounded-lg">
                {musicTaste.top_tracks[timeRange].map((track, index) => (
                  <div 
                    key={track.id} 
                    className="flex items-center p-3 border-b border-gray-800 last:border-b-0 hover:bg-gray-800 transition-colors"
                  >
                    <span className="text-gray-400 mr-4 w-6 text-right">
                      {index + 1}
                    </span>
                    {track.album.images?.[2] && (
                      <img 
                        src={track.album.images[2].url} 
                        alt={track.name} 
                        className="w-12 h-12 mr-4 rounded"
                      />
                    )}
                    <div>
                      <h3 className="font-bold">{track.name}</h3>
                      <p className="text-sm text-gray-400">
                        {track.artists.map(artist => artist.name).join(', ')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Recently Played Tab */}
          {activeTab === 'recent' && (
            <div className="bg-gray-900 rounded-lg">
              {musicTaste.recently_played.map((item, index) => (
                <div 
                  key={`${item.track.id}-${index}`} 
                  className="flex items-center p-3 border-b border-gray-800 last:border-b-0 hover:bg-gray-800 transition-colors"
                >
                  {item.track.album.images?.[2] && (
                    <img 
                      src={item.track.album.images[2].url} 
                      alt={item.track.name} 
                      className="w-12 h-12 mr-4 rounded"
                    />
                  )}
                  <div className="flex-grow">
                    <h3 className="font-bold">{item.track.name}</h3>
                    <p className="text-sm text-gray-400">
                      {item.track.artists.map(artist => artist.name).join(', ')}
                    </p>
                    <small className="text-xs text-gray-500">
                      {new Date(item.played_at).toLocaleString()}
                    </small>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Playlists Tab */}
          {activeTab === 'playlists' && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {musicTaste.playlists.map(playlist => (
                <div 
                  key={playlist.id} 
                  className="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-800 transition-colors"
                >
                  {playlist.images?.[0] && (
                    <img 
                      src={playlist.images[0].url} 
                      alt={playlist.name} 
                      className="w-full aspect-square object-cover"
                    />
                  )}
                  <div className="p-3">
                    <h3 className="font-bold text-sm truncate">{playlist.name}</h3>
                    <p className="text-xs text-gray-400">
                      {playlist.tracks.total} tracks
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Helper function to determine top genre from artists
function getTopGenre(artists) {
  const genreCounts = {};
  
  artists.forEach(artist => {
    artist.genres.forEach(genre => {
      genreCounts[genre] = (genreCounts[genre] || 0) + 1;
    });
  });
  
  return Object.entries(genreCounts)
    .sort((a, b) => b[1] - a[1])
    .map(entry => entry[0])[0] || 'Unknown';
}

export default Dashboard;