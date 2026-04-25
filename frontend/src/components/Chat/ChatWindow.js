import React, { useRef, useEffect } from 'react';
import { MessageBubble } from '../Message/MessageBubble';
import './ChatWindow.css';

export const ChatWindow = ({ messages, loading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="chat-window empty">
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <h2>Welcome to Chatbot</h2>
          <p>Start a conversation by asking a question below</p>
          <p className="empty-hint">Your chat history will be maintained during this session</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
          />
        ))}
        {loading && (
          <div className="loading-indicator">
            <span>Bot is thinking</span>
            <div className="typing-animation">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
