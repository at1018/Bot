import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
console.log('Using API URL:', API_URL);
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler
const handleError = (error) => {
  if (error.response) {
    throw new Error(error.response.data?.detail || 'API Error');
  } else if (error.request) {
    throw new Error('No response from server. Is the API running?');
  } else {
    throw error;
  }
};

export const chatService = {
  // Send a message and get response
  sendMessage: async (question, sessionId, context = null) => {
    try {
      const response = await apiClient.post('/api/chat', {
        question,
        session_id: sessionId,
        context,
      });
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  // Get conversation history for a session
  getConversationHistory: async (sessionId) => {
    try {
      const response = await apiClient.get(`/api/history/${sessionId}`);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  // Get session information
  getSessionInfo: async (sessionId) => {
    try {
      const response = await apiClient.get(`/api/session/${sessionId}`);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  // List all sessions
  listAllSessions: async () => {
    try {
      const response = await apiClient.get('/api/sessions');
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  // Clear session history
  clearSessionHistory: async (sessionId) => {
    try {
      const response = await apiClient.delete(`/api/history/${sessionId}`);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  // Delete entire session
  deleteSession: async (sessionId) => {
    try {
      const response = await apiClient.delete(`/api/session/${sessionId}`);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  // Get health status
  getHealthStatus: async () => {
    try {
      const response = await apiClient.get('/api/health');
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  // Get model information
  getModelInfo: async () => {
    try {
      const response = await apiClient.get('/api/info');
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
};
