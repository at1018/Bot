import React, { createContext, useContext, useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

const ChatContext = createContext();

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  // Session management
  const [sessionId, setSessionId] = useState(() => {
    const saved = localStorage.getItem('chatbot_session_id');
    return saved || uuidv4();
  });

  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);

  // Save session ID to localStorage
  React.useEffect(() => {
    localStorage.setItem('chatbot_session_id', sessionId);
  }, [sessionId]);

  // Add message to the chat
  const addMessage = useCallback((role, content) => {
    const message = {
      id: uuidv4(),
      role,
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, message]);
    return message;
  }, []);

  // Create new session
  const createNewSession = useCallback(() => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    setMessages([]);
    setError(null);
    return newSessionId;
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Set loading state
  const setLoadingState = useCallback((isLoading) => {
    setLoading(isLoading);
  }, []);

  // Set model info
  const setModelInfoData = useCallback((info) => {
    setModelInfo(info);
  }, []);

  // Set session info
  const setSessionInfoData = useCallback((info) => {
    setSessionInfo(info);
  }, []);

  // Set conversations list
  const setConversationsList = useCallback((list) => {
    setConversations(list);
  }, []);

  // Set error message
  const setErrorMessage = useCallback((errorMsg) => {
    setError(errorMsg);
  }, []);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const value = {
    // State
    sessionId,
    messages,
    loading,
    error,
    conversations,
    sessionInfo,
    modelInfo,
    
    // Actions
    setSessionId,
    addMessage,
    createNewSession,
    clearError,
    setLoadingState,
    setModelInfoData,
    setSessionInfoData,
    setConversationsList,
    setErrorMessage,
    clearMessages,
    setMessages,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};
