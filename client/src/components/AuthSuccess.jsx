
// components/AuthSuccess.js
import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function AuthSuccess() {
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    // Parse query parameters to get tokens
    const queryParams = new URLSearchParams(location.search);
    const accessToken = queryParams.get('access_token');
    const refreshToken = queryParams.get('refresh_token');
    
    if (accessToken && refreshToken) {
      // Store tokens in localStorage (in production, consider more secure options)
      localStorage.setItem('spotifyAccessToken', accessToken);
      localStorage.setItem('spotifyRefreshToken', refreshToken);
      
      // Redirect to dashboard
      navigate('/dashboard');
    } else {
      // Handle error
      navigate('/?error=authentication_failed');
    }
  }, [location, navigate]);
  
  return (
    <div className="auth-success">
      <h2>Authentication Successful</h2>
      <p>Redirecting to your dashboard...</p>
    </div>
  );
}

export default AuthSuccess;
