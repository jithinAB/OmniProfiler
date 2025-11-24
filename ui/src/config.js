// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// In development, the proxy handles routing to localhost:8000
// In production, set VITE_API_URL environment variable to your API endpoint

export const API_ENDPOINTS = {
    profileCode: `${API_BASE_URL}/profile/code`,
    profileFile: `${API_BASE_URL}/profile/file`,
    profileRepo: `${API_BASE_URL}/profile/repo`,
    history: `${API_BASE_URL}/history`
};

export default API_BASE_URL;
