import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { ChatMessage } from './ChatMessage';
import './MessageBubble.css';

export const MessageBubble = ({ role, content, timestamp }) => {
  const isUser = role === 'human';
  const timeAgo = timestamp
    ? formatDistanceToNow(new Date(timestamp), { addSuffix: true })
    : '';

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
      <div className="message-content">
        <ChatMessage content={content} isUser={isUser} />
      </div>
      {timestamp && <span className="message-time">{timeAgo}</span>}
    </div>
  );
};
