import { useCallback } from 'react';
import { useChatContext } from '../context/ChatContext';
import { chatService } from '../services/chatService';

export const useChat = () => {
  const {
    sessionId,
    messages,
    loading,
    error,
    addMessage,
    setLoadingState,
    setErrorMessage,
    clearError,
  } = useChatContext();

  const sendMessage = useCallback(
    async (question, context = null) => {
      try {
        clearError();
        setLoadingState(true);

        // Add user message to UI
        addMessage('human', question);

        // Send to API
        const response = await chatService.sendMessage(question, sessionId, context);

        // Add bot response to UI
        addMessage('assistant', response.answer);

        return response;
      } catch (err) {
        const errorMsg = err.message || 'Failed to send message';
        setErrorMessage(errorMsg);
        console.error('Error sending message:', err);
      } finally {
        setLoadingState(false);
      }
    },
    [sessionId, addMessage, setLoadingState, setErrorMessage, clearError]
  );

  const loadConversationHistory = useCallback(async () => {
    try {
      clearError();
      setLoadingState(true);
      const history = await chatService.getConversationHistory(sessionId);
      return history;
    } catch (err) {
      // Silently ignore "no history" errors - normal for new sessions
      console.debug('No history found (expected for new sessions):', err.message);
    } finally {
      setLoadingState(false);
    }
  }, [sessionId, setLoadingState, clearError]);

  const loadSessionInfo = useCallback(async () => {
    try {
      const info = await chatService.getSessionInfo(sessionId);
      return info;
    } catch (err) {
      console.error('Error loading session info:', err);
      return null;
    }
  }, [sessionId]);

  const loadAllConversations = useCallback(async () => {
    try {
      clearError();
      setLoadingState(true);
      const data = await chatService.listAllSessions();
      return data;
    } catch (err) {
      console.error('Error loading conversations:', err);
      return { total_sessions: 0, sessions: [] };
    } finally {
      setLoadingState(false);
    }
  }, [setLoadingState, clearError]);

  const clearCurrentSessionHistory = useCallback(async () => {
    try {
      clearError();
      const result = await chatService.clearSessionHistory(sessionId);
      return result;
    } catch (err) {
      const errorMsg = err.message || 'Failed to clear history';
      setErrorMessage(errorMsg);
      console.error('Error clearing history:', err);
    }
  }, [sessionId, setErrorMessage, clearError]);

  const deleteCurrentSession = useCallback(async () => {
    try {
      clearError();
      const result = await chatService.deleteSession(sessionId);
      return result;
    } catch (err) {
      const errorMsg = err.message || 'Failed to delete session';
      setErrorMessage(errorMsg);
      console.error('Error deleting session:', err);
    }
  }, [sessionId, setErrorMessage, clearError]);

  const loadModelInfo = useCallback(async () => {
    try {
      const info = await chatService.getModelInfo();
      return info;
    } catch (err) {
      console.error('Error loading model info:', err);
      return null;
    }
  }, []);

  const checkHealth = useCallback(async () => {
    try {
      const status = await chatService.getHealthStatus();
      return status;
    } catch (err) {
      console.error('Error checking health:', err);
      return null;
    }
  }, []);

  return {
    sessionId,
    messages,
    loading,
    error,
    sendMessage,
    loadConversationHistory,
    loadSessionInfo,
    loadAllConversations,
    clearCurrentSessionHistory,
    deleteCurrentSession,
    loadModelInfo,
    checkHealth,
  };
};
