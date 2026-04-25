# React Chatbot Frontend

A modern React UI for the LangChain-powered chatbot API.

## Folder Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatWindow.js
│   │   │   ├── ChatWindow.css
│   │   │   ├── InputArea.js
│   │   │   └── InputArea.css
│   │   ├── Message/
│   │   │   ├── MessageBubble.js
│   │   │   └── MessageBubble.css
│   │   └── Sidebar/
│   │       ├── Sidebar.js
│   │       └── Sidebar.css
│   ├── context/
│   │   └── ChatContext.js
│   ├── hooks/
│   │   └── useChat.js
│   ├── pages/
│   ├── services/
│   │   └── chatService.js
│   ├── styles/
│   │   └── index.css
│   ├── utils/
│   │   └── helpers.js
│   ├── App.js
│   ├── App.css
│   └── index.js
├── .env.example
├── package.json
└── README.md
```

## Installation

```bash
cd frontend
npm install
```

## Setup Environment

```bash
# Copy example env
copy .env.example .env

# Edit .env and set your API URL
# REACT_APP_API_URL=http://localhost:8000
```

## Running the App

```bash
npm start
```

The app will open at `http://localhost:3000`

## Features

- 💬 Real-time chat with conversation history
- 🔄 Session management
- 📱 Responsive mobile design
- 🎨 Modern UI with dark/light theme support
- ⚡ Fast API integration
- 💾 Local storage for session persistence
- 🔔 Real-time status indicators

## Components

### Sidebar
- Displays model information
- Shows current session details
- Lists recent conversations
- Navigation between sessions

### ChatWindow
- Displays conversation messages
- Auto-scrolling to latest message
- Typing indicator animation
- Empty state UI

### InputArea
- Message input field
- Optional context input
- Send button
- New session button

### MessageBubble
- User and bot message styling
- Timestamp display
- Smooth animations

## State Management

Uses React Context API for state management:
- Session ID
- Messages
- Loading state
- Error handling
- Model/Session info

## Hooks

### useChat
Custom hook for all chat operations:
- `sendMessage(question, context)`
- `loadConversationHistory()`
- `loadSessionInfo()`
- `loadAllConversations()`
- `clearCurrentSessionHistory()`
- `deleteCurrentSession()`

## API Integration

Communicates with the FastAPI backend:
- `POST /api/chat` - Send message
- `GET /api/history/{session_id}` - Get history
- `GET /api/session/{session_id}` - Get session info
- `GET /api/sessions` - List all sessions
- `DELETE /api/history/{session_id}` - Clear history
- `GET /api/health` - Health check
- `GET /api/info` - Model info

## Styling

Custom CSS with:
- CSS Variables for theming
- Responsive design
- Smooth animations
- Modern gradient backgrounds
- Accessibility features

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimizations

- Lazy loading messages
- Memoized components
- Efficient state updates
- Auto-scrolling optimization
- Debounced API calls

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Message search
- [ ] Export conversations
- [ ] User authentication
- [ ] Conversation analytics
- [ ] File upload support
- [ ] Voice input/output
- [ ] Message editing
