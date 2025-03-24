// components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [profile, setProfile] = useState(null);
  const [musicTaste, setMusicTaste] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('medium_term'); // Add this line
  
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  useEffect(() => {
    // Check if user is authenticated
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
    return <div className="loading">Loading your music profile...</div>;
  }
  
  if (error) {
    return <div className="error">Error: {error}</div>;
  }
  
  return (
    <div className="dashboard">
      {profile && (
        <div className="user-profile">
          {profile.images && profile.images.length > 0 && (
            <img 
              src={profile.images[0].url} 
              alt={profile.display_name} 
              className="profile-image" 
            />
          )}
          <h1>Welcome, {profile.display_name}</h1>
          <button onClick={logout} className="logout-button">Logout</button>
        </div>
      )}
      
      <div className="tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''} 
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'artists' ? 'active' : ''} 
          onClick={() => setActiveTab('artists')}
        >
          Top Artists
        </button>
        <button 
          className={activeTab === 'tracks' ? 'active' : ''} 
          onClick={() => setActiveTab('tracks')}
        >
          Top Tracks
        </button>
        <button 
          className={activeTab === 'recent' ? 'active' : ''} 
          onClick={() => setActiveTab('recent')}
        >
          Recently Played
        </button>
        <button 
          className={activeTab === 'playlists' ? 'active' : ''} 
          onClick={() => setActiveTab('playlists')}
        >
          Playlists
        </button>
      </div>
      
      <div className="tab-content">
        {musicTaste && (
          <>
            {activeTab === 'overview' && (
              <div className="overview">
                <h2>Your Music Taste Analysis</h2>
                <div className="stats-grid">
                  <div className="stat-card">
                    <h3>Top Genre</h3>
                    <p>{getTopGenre(musicTaste.top_artists.medium_term)}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Top Artist</h3>
                    <p>{musicTaste.top_artists.medium_term[0]?.name || 'None'}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Top Track</h3>
                    <p>{musicTaste.top_tracks.medium_term[0]?.name || 'None'}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Playlists</h3>
                    <p>{musicTaste.playlists.length}</p>
                  </div>
                </div>
              </div>
            )}
            
            {activeTab === 'artists' && (
              <div className="artists">
                <h2>Your Top Artists</h2>
                <div className="time-range-tabs">
                  <button onClick={() => setTimeRange('short_term')}>Last Month</button>
                  <button onClick={() => setTimeRange('medium_term')}>Last 6 Months</button>
                  <button onClick={() => setTimeRange('long_term')}>All Time</button>
                </div>
                <div className="artists-grid">
                  {musicTaste.top_artists[timeRange].map(artist => (
                    <div key={artist.id} className="artist-card">
                      {artist.images && artist.images.length > 0 && (
                        <img src={artist.images[0].url} alt={artist.name} />
                      )}
                      <h3>{artist.name}</h3>
                      <p>Genres: {artist.genres.slice(0, 3).join(', ')}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'tracks' && (
              <div className="tracks">
                <h2>Your Top Tracks</h2>
                <div className="time-range-tabs">
                  <button onClick={() => setTimeRange('short_term')}>Last Month</button>
                  <button onClick={() => setTimeRange('medium_term')}>Last 6 Months</button>
                  <button onClick={() => setTimeRange('long_term')}>All Time</button>
                </div>
                <div className="tracks-list">
                  {musicTaste.top_tracks[timeRange].map((track, index) => (
                    <div key={track.id} className="track-item">
                      <span className="track-number">{index + 1}</span>
                      {track.album.images && track.album.images.length > 0 && (
                        <img src={track.album.images[2].url} alt={track.name} className="track-image" />
                      )}
                      <div className="track-info">
                        <h3>{track.name}</h3>
                        <p>{track.artists.map(artist => artist.name).join(', ')}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'recent' && (
              <div className="recent">
                <h2>Recently Played</h2>
                <div className="tracks-list">
                  {musicTaste.recently_played.map((item, index) => (
                    <div key={`${item.track.id}-${index}`} className="track-item">
                      {item.track.album.images && item.track.album.images.length > 0 && (
                        <img src={item.track.album.images[2].url} alt={item.track.name} className="track-image" />
                      )}
                      <div className="track-info">
                        <h3>{item.track.name}</h3>
                        <p>{item.track.artists.map(artist => artist.name).join(', ')}</p>
                        <small>Played: {new Date(item.played_at).toLocaleString()}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'playlists' && (
              <div className="playlists">
                <h2>Your Playlists</h2>
                <div className="playlists-grid">
                  {musicTaste.playlists.map(playlist => (
                    <div key={playlist.id} className="playlist-card">
                      {playlist.images && playlist.images.length > 0 && (
                        <img src={playlist.images[0].url} alt={playlist.name} />
                      )}
                      <h3>{playlist.name}</h3>
                      <p>{playlist.tracks.total} tracks</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// Helper function to determine top genre from artists
function getTopGenre(artists) {
  // Create a map to count genre occurrences
  const genreCounts = {};
  
  artists.forEach(artist => {
    artist.genres.forEach(genre => {
      genreCounts[genre] = (genreCounts[genre] || 0) + 1;
    });
  });
  
  // Find the genre with highest count
  return Object.entries(genreCounts)
    .sort((a, b) => b[1] - a[1])
    .map(entry => entry[0])[0] || 'Unknown';
}

export default Dashboard;