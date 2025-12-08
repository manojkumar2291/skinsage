import axiosClient from './axiosClient';

/**
 * Login with email and password
 * @param {Object} credentials
 * @param {string} credentials.username - Email
 * @param {string} credentials.password - Password
 * @returns {Promise<{access_token: string, refresh_token: string, token_type: string}>}
 */
export const login = async (credentials) => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await axiosClient.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  // Store tokens
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
  }
  if (response.data.refresh_token) {
    localStorage.setItem('refresh_token', response.data.refresh_token);
  }
  
  return response.data;
};

/**
 * Register a new user
 * @param {Object} userData
 * @param {string} userData.email
 * @param {string} userData.password
 * @param {string} userData.full_name
 * @param {string} userData.role - 'patient' or 'provider'
 * @returns {Promise}
 */
export const register = async (userData) => {
  const response = await axiosClient.post('/api/auth/register', userData);
  return response.data;
};

/**
 * Google OAuth login
 * @param {string} token - Google OAuth token
 * @returns {Promise}
 */
export const googleLogin = async (token) => {
  const response = await axiosClient.post('/api/auth/google-login', { token });
  
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
  }
  if (response.data.refresh_token) {
    localStorage.setItem('refresh_token', response.data.refresh_token);
  }
  
  return response.data;
};

/**
 * Get current user information
 * @returns {Promise}
 */
export const getCurrentUser = async () => {
  const response = await axiosClient.get('/api/auth/me');
  console.log('getCurrentUser response:', response);
  return response.data;
};

/**
 * Complete user profile
 * @param {Object} profileData
 * @param {string} profileData.phone
 * @param {string} profileData.date_of_birth - ISO date string
 * @param {string} profileData.gender - 'male', 'female', 'other'
 * @returns {Promise}
 */
export const completeProfile = async (profileData) => {
  const response = await axiosClient.put('/api/auth/complete-profile', profileData);
  return response.data;
};

/**
 * Accept consent (privacy/terms)
 * @returns {Promise}
 */
export const acceptConsent = async () => {
  const response = await axiosClient.post('/api/auth/consent');
  return response.data;
};

/**
 * Logout user
 */
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
};

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};