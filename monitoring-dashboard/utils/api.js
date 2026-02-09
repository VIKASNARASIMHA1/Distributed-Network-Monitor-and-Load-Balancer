import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Handle unauthorized
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          console.error('Forbidden:', data);
          break;
        case 404:
          console.error('Not Found:', data);
          break;
        case 500:
          console.error('Server Error:', data);
          break;
        default:
          console.error(`Error ${status}:`, data);
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response received:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
export const loadBalancerAPI = {
  // Get load balancer stats
  getStats: () => api.get('/stats'),
  
  // Get servers list
  getServers: () => api.get('/servers'),
  
  // Send test request
  sendRequest: () => api.get('/request'),
  
  // Change algorithm
  changeAlgorithm: (algorithm) => api.get(`/algorithm/${algorithm}`),
  
  // Get metrics
  getMetrics: () => api.get('/metrics'),
  
  // Get health status
  getHealth: () => api.get('/health'),
};

export const serverAPI = {
  // Get server info
  getServerInfo: (serverId) => api.get(`/server/${serverId}/info`),
  
  // Get server metrics
  getServerMetrics: (serverId) => api.get(`/server/${serverId}/metrics`),
  
  // Restart server
  restartServer: (serverId) => api.post(`/server/${serverId}/restart`),
};

// WebSocket utility
export const createWebSocket = (url) => {
  const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:5000/ws';
  const socket = new WebSocket(wsUrl);
  
  return {
    socket,
    
    onOpen: (callback) => {
      socket.addEventListener('open', callback);
    },
    
    onMessage: (callback) => {
      socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          callback(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      });
    },
    
    onError: (callback) => {
      socket.addEventListener('error', callback);
    },
    
    onClose: (callback) => {
      socket.addEventListener('close', callback);
    },
    
    send: (data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else {
        console.error('WebSocket is not open');
      }
    },
    
    close: () => {
      socket.close();
    },
    
    isConnected: () => socket.readyState === WebSocket.OPEN,
  };
};

export default api;