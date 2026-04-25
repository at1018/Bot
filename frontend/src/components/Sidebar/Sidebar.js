import React, { useState, useEffect } from 'react';
import { FiMenu, FiX, FiTrash2, FiRefreshCw, FiSettings } from 'react-icons/fi';
import { useChat } from '../../hooks/useChat';
import { useChatContext } from '../../context/ChatContext';
import './Sidebar.css';

export const Sidebar = ({ onSessionChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const { loadAllConversations, loadSessionInfo, loadModelInfo, checkHealth } = useChat();
  const { sessionId } = useChatContext();

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, [sessionId]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [allConversations, info, model] = await Promise.all([
        loadAllConversations(),
        loadSessionInfo(),
        loadModelInfo(),
      ]);
      
      if (allConversations) {
        setConversations(allConversations.sessions || []);
      }
      if (info) {
        setSessionInfo(info);
      }
      if (model) {
        setModelInfo(model);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const closeSidebar = () => {
    setIsOpen(false);
  };

  return (
    <>
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h1>Chatbot</h1>
          <button className="close-btn" onClick={closeSidebar}>
            <FiX size={20} />
          </button>
        </div>



        {/* Conversations */}
        <div className="sidebar-section">
          <div className="section-header">
            <h3>Conversations</h3>
            <button
              className="refresh-btn"
              onClick={loadData}
              disabled={isLoading}
              title="Refresh conversations"
            >
              <FiRefreshCw size={16} />
            </button>
          </div>

          {conversations.length > 0 ? (
            <div className="conversations-list">
              {conversations.slice(0, 5).map((conv) => (
                <div
                  key={conv.session_id}
                  className={`conversation-item ${conv.session_id === sessionId ? 'active' : ''}`}
                  onClick={() => {
                    onSessionChange(conv.session_id);
                    closeSidebar();
                  }}
                >
                  <div className="conv-info">
                    <span className="conv-count">{conv.message_count} messages</span>
                    <span className="conv-time">
                      {new Date(conv.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <span className="conv-id">{conv.session_id.substring(0, 8)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-conversations">No conversations yet</p>
          )}
        </div>

        {/* Settings */}
        <div className="sidebar-footer">
          <button className="settings-btn" title="Settings">
            <FiSettings size={18} />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {isOpen && <div className="sidebar-overlay" onClick={closeSidebar} />}
    </>
  );
};
