import React, { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar/Sidebar';
import { ChatWindow } from './components/Chat/ChatWindow';
import { InputArea } from './components/Chat/InputArea';
import { ChatProvider, useChatContext } from './context/ChatContext';
import { useChat } from './hooks/useChat';
import './App.css';

function AppContent() {
  const {
    sessionId,
    messages,
    loading,
    error,
    createNewSession,
    setMessages,
    setSessionId,
  } = useChatContext();

  const {
    sendMessage,
    loadConversationHistory,
    checkHealth,
  } = useChat();

  const [apiHealth, setApiHealth] = useState(null);

  // Check API health and load conversation history on mount/session change
  useEffect(() => {
    const initialize = async () => {
      // Check health
      const health = await checkHealth();
      setApiHealth(health);

      if (!health) {
        console.warn('API is not responding');
        return;
      }

      // Load conversation history
      const history = await loadConversationHistory();
      if (history && history.messages) {
        const loadedMessages = history.messages.map((msg) => ({
          id: msg.id || `${msg.role}-${Math.random()}`,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
        }));
        setMessages(loadedMessages);
      }
    };

    initialize();
  }, [sessionId]);

  const handleNewSession = () => {
    createNewSession();
  };

  const handleSessionChange = (newSessionId) => {
    setSessionId(newSessionId);
  };

  return (
    <div className="app">
      <Sidebar onSessionChange={handleSessionChange} />

      <div className="main-container">
        {/* Health Status */}
        {!apiHealth && (
          <div className="error-banner">
            <span>⚠️ API is not responding. Please ensure the server is running on http://localhost:8000</span>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-banner">
            <span>❌ {error}</span>
          </div>
        )}

        {/* Chat Interface */}
        <div className="chat-container">
          <ChatWindow messages={messages} loading={loading} />
          <InputArea
            onSendMessage={sendMessage}
            onNewSession={handleNewSession}
            loading={loading}
            disabled={!apiHealth}
          />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <ChatProvider>
      <AppContent />
    </ChatProvider>
  );
}

export default App;
