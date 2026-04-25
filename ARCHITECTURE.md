# Chatbot Project - Complete Architecture Guide

## Overview

Your chatbot project consists of two main parts:

1. **Backend** (Python/FastAPI) - API Server
2. **Frontend** (React) - User Interface

## Backend Architecture

### Technology Stack
- **FastAPI** - Modern web framework
- **LangChain** - LLM orchestration
- **OpenAI** - Language model
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Folder Structure
```
Bot/
├── app/
│   ├── api/
│   │   └── routes.py           # API endpoints (chat, history, sessions)
│   ├── core/
│   │   ├── llm.py              # LLM configuration with context awareness
│   │   └── memory.py           # Session and conversation memory management
│   ├── schemas/
│   │   └── chat.py             # Pydantic models (request/response)
│   ├── utils/
│   │   └── logger.py           # Logging configuration
│   └── __init__.py
├── config/
│   └── settings.py             # Environment settings
├── main.py                     # FastAPI app initialization
├── requirements.txt
├── .env                        # Environment variables
└── logs/                       # Application logs
```

### How Backend Works

#### 1. API Endpoints
```
POST   /api/chat                  → Send message with context awareness
GET    /api/history/{session_id}  → Retrieve conversation history
GET    /api/session/{session_id}  → Get session info
GET    /api/sessions              → List all active sessions
DELETE /api/history/{session_id}  → Clear session history
DELETE /api/session/{session_id}  → Delete entire session
GET    /api/health                → Health check
GET    /api/info                  → Model information
```

#### 2. Message Flow
```
User Question
    ↓
API receives /api/chat request
    ↓
Memory retrieves last 5 messages from session
    ↓
LLM processes question + conversation context
    ↓
OpenAI generates answer
    ↓
Memory stores human + assistant message
    ↓
Response sent to frontend with history_used flag
```

#### 3. Session Management
- Each conversation has a unique Session ID (UUID)
- Messages stored in-memory (ConversationMemory)
- Last 5 messages used for context in LLM prompts
- Sessions persist for the API lifetime
- Max 50 messages per session (configurable)

#### 4. Context Awareness
```
First Message:
  Q: "What is Python?"
  history_used: false

Second Message:
  Q: "What are its advantages?"
  Bot includes previous Q&A in system prompt
  history_used: true
  Answer considers Python context

Third Message:
  Q: "How to install it?"
  Bot includes conversation history
  history_used: true
  Answer provides Python-specific setup
```

---

## Frontend Architecture

### Technology Stack
- **React** 18 - UI Library
- **Axios** - HTTP Client
- **React Icons** - Icon Library
- **date-fns** - Date formatting
- **Context API** - State Management

### Folder Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatWindow.js      # Message display area
│   │   │   ├── ChatWindow.css
│   │   │   ├── InputArea.js       # Input field + buttons
│   │   │   └── InputArea.css
│   │   ├── Message/
│   │   │   ├── MessageBubble.js   # Individual message
│   │   │   └── MessageBubble.css
│   │   └── Sidebar/
│   │       ├── Sidebar.js        # Navigation + info
│   │       └── Sidebar.css
│   ├── context/
│   │   └── ChatContext.js        # Global state (Context API)
│   ├── hooks/
│   │   └── useChat.js            # Custom hook for chat logic
│   ├── services/
│   │   └── chatService.js        # API calls
│   ├── styles/
│   │   └── index.css             # Global styles
│   ├── utils/
│   │   └── helpers.js            # Utility functions
│   ├── App.js                    # Main component
│   ├── App.css
│   └── index.js                  # React DOM render
├── .env
├── .env.example
├── .gitignore
├── package.json
└── README.md
```

### State Management (Context API)

**ChatContext** stores and manages:
```javascript
{
  sessionId,           // Current session UUID
  messages,           // Array of messages
  loading,            // Loading state
  error,              // Error messages
  conversations,      // List of all sessions
  sessionInfo,        // Current session details
  modelInfo,          // LLM model info
}
```

### Component Architecture

```
App
├── Sidebar
│   ├── Model Info
│   ├── Session Info
│   └── Conversations List
└── Main Container
    ├── Error Banner (conditional)
    └── Chat Container
        ├── ChatWindow
        │   ├── MessageBubble (user)
        │   ├── MessageBubble (bot)
        │   └── Loading Indicator
        └── InputArea
            ├── Context Input (optional)
            ├── Message Input
            ├── Send Button
            └── New Session Button
```

### Data Flow

```
1. User Types Message
   ↓
2. InputArea captures input
   ↓
3. OnSend triggers useChat.sendMessage()
   ↓
4. Add user message to UI
   ↓
5. Call chatService.sendMessage() → API
   ↓
6. API processes and returns response
   ↓
7. Add bot message to UI
   ↓
8. Messages auto-scroll to bottom
```

### Hooks

**useChat** provides all chat operations:
```javascript
const {
  sessionId,
  messages,
  loading,
  error,
  sendMessage,                    // Send message to API
  loadConversationHistory,        // Load conversation history
  loadSessionInfo,                // Get session details
  loadAllConversations,           // Get all sessions
  clearCurrentSessionHistory,     // Clear messages but keep session
  deleteCurrentSession,           // Delete entire session
  loadModelInfo,                  // Get model configuration
  checkHealth,                    // Verify API is running
} = useChat();
```

### Services

**chatService** handles all API communication:
```javascript
chatService.sendMessage(question, sessionId, context)
chatService.getConversationHistory(sessionId)
chatService.getSessionInfo(sessionId)
chatService.listAllSessions()
chatService.clearSessionHistory(sessionId)
chatService.deleteSession(sessionId)
chatService.getHealthStatus()
chatService.getModelInfo()
```

---

## How They Work Together

### Complete Message Journey

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. User types "What is Python?"                        │
│     ↓                                                     │
│  2. InputArea.js captures input                         │
│     ↓                                                     │
│  3. onSendMessage → useChat.sendMessage()               │
│     ↓                                                     │
│  4. addMessage('human', 'What is Python?')              │
│     ↓                                                     │
│  5. chatService.sendMessage() → HTTP POST               │
│                                                           │
└───────────────────────|────────────────────────────────┘
                        ↓ (HTTP Request)
                   
                   http://localhost:8000/api/chat
                   
                   {
                     "question": "What is Python?",
                     "session_id": "uuid-123",
                     "context": null
                   }

┌─────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  6. POST /api/chat endpoint receives request            │
│     ↓                                                     │
│  7. SessionId = "uuid-123" (from request)               │
│     ↓                                                     │
│  8. memory.get_history_text(session_id, limit=5)        │
│     → Returns "" (first message, no history)            │
│     ↓                                                     │
│  9. llm.get_answer(question, context, history)          │
│     ↓                                                     │
│  10. LangChain processes:                               │
│      - System prompt + context + history                │
│      - Question: "What is Python?"                      │
│      ↓                                                    │
│  11. OpenAI API call                                    │
│      ↓                                                    │
│  12. Response: "Python is a high-level..."              │
│      ↓                                                    │
│  13. memory.add_message(session_id, 'human', question)  │
│      memory.add_message(session_id, 'assistant', answer)│
│      ↓                                                    │
│  14. Return MessageResponse                             │
│      {                                                    │
│        "question": "What is Python?",                   │
│        "answer": "Python is...",                        │
│        "session_id": "uuid-123",                        │
│        "history_used": false,                           │
│        "timestamp": "2024-01-15T..."                    │
│      }                                                    │
│                                                           │
└───────────────────────|────────────────────────────────┘
                        ↓ (HTTP Response)

┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  15. Response received by chatService                    │
│      ↓                                                    │
│  16. addMessage('assistant', response.answer)           │
│      ↓                                                    │
│  17. ChatWindow re-renders with new message             │
│      ↓                                                    │
│  18. Auto-scroll to latest message                      │
│      ↓                                                    │
│  19. Stop loading indicator                             │
│                                                           │
│  ✅ User sees bot response                              │
│                                                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   NEXT MESSAGE (Context Aware)          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  20. User asks: "What are its advantages?"              │
│      ↓                                                    │
│  21. Same flow, but this time:                          │
│      memory.get_history_text(session_id, limit=5)       │
│      → Returns previous Q&A                             │
│      ↓                                                    │
│  22. LLM processes with context:                        │
│      "Q1: What is Python?"                              │
│      "A1: Python is..."                                 │
│      "Q2: What are its advantages?"                     │
│      ↓                                                    │
│  23. Bot provides advantages in Python context          │
│      history_used: true                                 │
│      ✅ Context-aware response!                         │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Installation & Running

### 1. Backend Setup

```bash
cd Bot

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup .env
copy .env.example .env
# Edit .env and add OPENAI_API_KEY

# Run server
python main.py
```

Backend runs on: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup .env
copy .env.example .env

# Run development server
npm start
```

Frontend runs on: `http://localhost:3000`

### 3. Verify Connection

- Open http://localhost:3000
- Sidebar shows model info if API is running
- Try sending a message
- Check browser console for errors

---

## Key Features Explained

### Session Management
- Each user conversation is a separate session
- Session ID saved in localStorage
- Reload page → same session continues
- Start new session button → new UUID

### Conversation History
- Messages stored on backend in-memory
- Retrievable via /api/history/{session_id}
- Visible in sidebar (recent conversations)
- Last 5 messages used for context

### Context Awareness
- LLM receives message + last 5 messages
- Bot understands conversation context
- Response is aware of previous messages
- `history_used` flag shows if context was used

### Error Handling
- API down → error banner shown
- Invalid input → error message displayed
- Failed API call → retry or show error
- Toast-like notifications for user feedback

### Mobile Responsive
- Sidebar collapses on mobile
- Chat window full width
- Touch-friendly buttons
- Optimized for small screens

---

## Configuration

### Backend (.env)
```
OPENAI_API_KEY=sk-xxxx
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

---

## API Response Examples

### Chat Response
```json
{
  "question": "What is Python?",
  "answer": "Python is a high-level programming language...",
  "model": "gpt-3.5-turbo",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00",
  "history_used": false
}
```

### Conversation History
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "human",
      "content": "What is Python?",
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "role": "assistant",
      "content": "Python is...",
      "timestamp": "2024-01-15T10:30:05"
    }
  ],
  "message_count": 2,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:05"
}
```

---

## Performance Optimizations

### Frontend
- Lazy component loading
- Memoized components
- Debounced API calls
- Auto-scroll optimization
- Message virtualization (ready for large conversations)

### Backend
- In-memory storage (fast)
- Limited history window (5 messages)
- Message limit per session (50 messages)
- Async API handlers
- Efficient context trimming

---

## Future Enhancements

1. **Persistence**
   - MongoDB/PostgreSQL for persistent storage
   - Conversation export (JSON/PDF)

2. **Features**
   - Dark mode toggle
   - Message search
   - Conversation analytics
   - User authentication

3. **Advanced**
   - WebSocket for real-time chat
   - File upload support
   - Voice input/output
   - Multiple LLM providers

4. **Deployment**
   - Docker containerization
   - Cloud deployment (AWS, Azure, GCP)
   - CI/CD pipeline
   - Monitoring and logging

---

## Troubleshooting

### API Not Responding
```
Error: "No response from server"
Solution: 
  1. Check if backend is running (python main.py)
  2. Verify OPENAI_API_KEY is set
  3. Check http://localhost:8000/health
```

### No Messages Loading
```
Error: Messages aren't showing
Solution:
  1. Check browser console for errors
  2. Verify API URL in .env
  3. Check session ID is persisting
  4. Clear localStorage and reload
```

### Context Not Being Used
```
Issue: history_used always false
Solution:
  1. Send at least 2 messages in same session
  2. Check session ID matches in requests
  3. Verify API is storing messages
  4. Call GET /api/history/{session_id}
```

---

## Summary

Your chatbot project is a full-stack application:

**Backend** - Provides intelligent responses with context awareness via LLM API  
**Frontend** - Beautiful React UI for seamless user interaction  
**Integration** - FastAPI + React via REST API with session management  
**Result** - Conversational AI that remembers context from previous messages

Happy coding! 🚀
