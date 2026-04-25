import React, { useState } from 'react';
import { FiSend, FiPlusCircle } from 'react-icons/fi';
import './InputArea.css';

export const InputArea = ({ onSendMessage, onNewSession, loading, disabled }) => {
  const [input, setInput] = useState('');
  const [context, setContext] = useState('');
  const [showContext, setShowContext] = useState(false);

  const handleSend = () => {
    if (input.trim() && !loading && !disabled) {
      onSendMessage(input.trim(), context.trim() || null);
      setInput('');
      setContext('');
      setShowContext(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading && !disabled) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-area">
      {showContext && (
        <div className="context-input-wrapper">
          <input
            type="text"
            placeholder="Add context for better answers (optional)"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="context-input"
            disabled={loading || disabled}
          />
        </div>
      )}

      <div className="input-wrapper">
        <button
          onClick={() => setShowContext(!showContext)}
          className="context-toggle-btn"
          title={showContext ? 'Hide context' : 'Add context'}
          disabled={loading || disabled}
        >
          {showContext ? '✓' : '+'}
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything..."
          className="message-input"
          disabled={loading || disabled}
        />

        <button
          onClick={handleSend}
          className="send-btn"
          disabled={!input.trim() || loading || disabled}
          title="Send message"
        >
          <FiSend size={20} />
        </button>

        <button
          onClick={onNewSession}
          className="new-session-btn"
          disabled={loading || disabled}
          title="Start new session"
        >
          <FiPlusCircle size={20} />
        </button>
      </div>

      <div className="input-hint">
        <span>Shift + Enter for new line</span>
      </div>
    </div>
  );
};
