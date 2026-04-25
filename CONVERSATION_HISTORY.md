# Conversation History & Session Management Guide

## Overview

The chatbot API now includes comprehensive conversation history and session management features, enabling context-aware responses to follow-up questions.

## Table of Contents

1. [Quick Start](#quick-start)
2. [How Sessions Work](#how-sessions-work)
3. [How Context Awareness Works](#how-context-awareness-works)
4. [API Endpoints](#api-endpoints)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Without Session (Stateless)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

### With Session (Stateful)
```bash
# First question
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "session_id": "my-session-123"
  }'

# Follow-up question (uses context from previous answer)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are its main advantages?",
    "session_id": "my-session-123"
  }'
```

## How Sessions Work

### Session Creation

Sessions are created automatically when you provide a `session_id` in the request. If no `session_id` is provided, a new UUID is generated.

```json
{
  "question": "What is machine learning?",
  "session_id": "unique-session-id-here"
}
```

### Session Structure

Each session stores:
- **Session ID**: Unique identifier for the conversation
- **Messages**: Array of human and assistant messages
- **Timestamps**: When each message was created
- **Metadata**: Session creation time, last update time, message count

### Session Lifecycle

1. **Creation**: First message in a session creates it
2. **Active**: Messages are added as conversation continues
3. **Maintenance**: History is limited to 50 messages per session (configurable)
4. **Retrieval**: Full history can be retrieved at any time
5. **Cleanup**: Sessions can be cleared or deleted manually

## How Context Awareness Works

### Behind the Scenes

When you ask a follow-up question:

1. **History Retrieval**: The system retrieves the last 5 messages from the session
2. **Context Building**: These messages are formatted and included in the system prompt
3. **LLM Processing**: The LLM receives the conversation context along with your new question
4. **Response Generation**: The response is generated with awareness of previous messages
5. **Storage**: Both your question and the response are stored in the session

### Example Conversation Flow

```
User: "What is Python?"
└─ Bot uses no context (first message)
   └─ Response: "Python is a high-level programming language..."

User: "What are its main advantages?"
└─ Bot includes context of previous exchange
   └─ Response includes Python-specific advantages

User: "How do I get started?"
└─ Bot considers Python context
   └─ Response includes Python-specific installation steps
```

### Context Limits

- **History Window**: Last 5 messages (user/assistant pairs)
- **Session Limit**: Max 50 messages per session (older ones are trimmed)
- **Timestamp**: Each message is timestamped for tracking

## API Endpoints

### Chat Endpoint (with History)

**Endpoint**: `POST /api/chat`

**Request**:
```json
{
  "question": "Your question here",
  "context": "Optional context",
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "question": "Your question here",
  "answer": "Bot's answer with context awareness",
  "model": "gpt-3.5-turbo",
  "session_id": "session-id-used",
  "timestamp": "2024-01-15T10:30:00",
  "history_used": true
}
```

**Key Points**:
- `session_id` is optional; UUID generated if not provided
- `history_used` is `true` if conversation history was leveraged
- Messages are automatically stored for future context

### Get Conversation History

**Endpoint**: `GET /api/history/{session_id}`

**Response**:
```json
{
  "session_id": "session-123",
  "messages": [
    {
      "role": "human",
      "content": "What is AI?",
      "timestamp": "2024-01-15T10:00:00"
    },
    {
      "role": "assistant",
      "content": "AI is the simulation of human intelligence...",
      "timestamp": "2024-01-15T10:00:05"
    }
  ],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:05",
  "message_count": 2
}
```

### Get Session Information

**Endpoint**: `GET /api/session/{session_id}`

**Response**:
```json
{
  "session_id": "session-123",
  "message_count": 10,
  "created_at": "2024-01-15T10:00:00",
  "last_message_at": "2024-01-15T10:30:00"
}
```

### List All Sessions

**Endpoint**: `GET /api/sessions`

**Response**:
```json
{
  "total_sessions": 3,
  "sessions": [
    {
      "session_id": "session-123",
      "message_count": 5,
      "created_at": "2024-01-15T10:00:00",
      "last_message_at": "2024-01-15T10:15:00"
    }
  ]
}
```

### Clear Session History

**Endpoint**: `DELETE /api/history/{session_id}`

Clears all messages from a session but keeps the session active.

**Response**:
```json
{
  "session_id": "session-123",
  "status": "success",
  "message": "Conversation history cleared for session session-123"
}
```

### Delete Session

**Endpoint**: `DELETE /api/session/{session_id}`

Completely removes a session and all its history.

**Response**:
```json
{
  "session_id": "session-123",
  "status": "success",
  "message": "Session session-123 deleted completely"
}
```

## Code Examples

### Python Example

```python
import requests
import uuid

BASE_URL = "http://localhost:8000"
session_id = str(uuid.uuid4())

def chat(question, context=None):
    """Send a question and get response with history"""
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "question": question,
            "context": context,
            "session_id": session_id
        }
    )
    return response.json()

def get_history():
    """Retrieve full conversation history"""
    response = requests.get(f"{BASE_URL}/api/history/{session_id}")
    return response.json()

# Example usage
print("Question 1:", chat("What is Python?")["answer"][:100], "...")
print("Question 2:", chat("What are its advantages?")["answer"][:100], "...")

# View history
history = get_history()
print(f"Session has {history['message_count']} messages")
```

### JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000";
const sessionId = generateUUID();

async function chat(question, context = null) {
    const response = await fetch(`${BASE_URL}/api/chat`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            question,
            context,
            session_id: sessionId
        })
    });
    return response.json();
}

async function getHistory() {
    const response = await fetch(`${BASE_URL}/api/history/${sessionId}`);
    return response.json();
}

// Usage
const answer1 = await chat("What is cloud computing?");
console.log(answer1.answer);

const answer2 = await chat("What are its benefits?");
console.log(`Used history: ${answer2.history_used}`);

const history = await getHistory();
console.log(`Total messages: ${history.message_count}`);
```

### Node.js/Express Middleware

```javascript
// Middleware to manage session in Express
const sessionMiddleware = (req, res, next) => {
    if (!req.headers['x-session-id']) {
        req.sessionId = uuid.v4();
        res.setHeader('x-session-id', req.sessionId);
    } else {
        req.sessionId = req.headers['x-session-id'];
    }
    next();
};

app.use(sessionMiddleware);

app.post('/ask', async (req, res) => {
    const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            question: req.body.question,
            session_id: req.sessionId
        })
    });
    const data = await response.json();
    res.json(data);
});
```

## Best Practices

### 1. Session Management

```python
# ✅ Good: Reuse session ID for related questions
session_id = "user-123-conversation"
chat("What is AI?", session_id)
chat("How is it used in healthcare?", session_id)

# ❌ Bad: Using different sessions for related questions
chat("What is AI?", "session-1")
chat("How is it used in healthcare?", "session-2")  # No context
```

### 2. Session Cleanup

```python
# ✅ Good: Clean up old sessions periodically
sessions = requests.get("http://localhost:8000/api/sessions").json()
for session in sessions['sessions']:
    if session['message_count'] > 100:
        requests.delete(f"http://localhost:8000/api/session/{session['session_id']}")
```

### 3. Error Handling

```python
# ✅ Good: Handle missing sessions gracefully
try:
    history = requests.get(f"http://localhost:8000/api/history/{session_id}").json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Session not found, starting new session")
        session_id = str(uuid.uuid4())
```

### 4. Context Usage

```python
# ✅ Good: Provide additional context when needed
chat("Compare Python and JavaScript", session_id, 
     context="I'm a beginner programmer")

# Better answers when additional context is provided
```

## Troubleshooting

### Session Not Found

**Error**: `"No conversation history found for session xyz"`

**Solution**:
```python
# Check if session exists
sessions = requests.get("http://localhost:8000/api/sessions").json()
session_ids = [s['session_id'] for s in sessions['sessions']]

if session_id not in session_ids:
    print(f"Session {session_id} doesn't exist")
    # Create new session by making a request with that session_id
```

### History Not Growing

**Issue**: Messages aren't being stored

**Causes**:
- Session ID not being passed consistently
- Session cleanup deleting old sessions
- Memory limits (50 messages per session)

**Solution**:
```python
# Verify session ID is consistent
response = chat("First question", session_id="my-session")
print(response['session_id'])  # Should be 'my-session'

# Check session info
info = requests.get(f"http://localhost:8000/api/session/my-session").json()
print(f"Message count: {info['message_count']}")
```

### No Context Being Used

**Issue**: `history_used` is always false

**Solution**:
```python
# Ensure same session is used for follow-up questions
# Check that messages are being stored
history = requests.get(f"http://localhost:8000/api/history/{session_id}").json()
print(f"Messages in history: {len(history['messages'])}")

# If empty, messages aren't being stored - check logs
```

## Performance Considerations

1. **Memory Usage**: Each session stores up to 50 messages in memory
2. **Context Window**: Only last 5 messages used for context (efficient)
3. **Message Retrieval**: Historical queries are fast (in-memory)
4. **Scalability**: For production, consider persistent storage (database)

## Next Steps

- Integrate with your frontend application
- Set up regular session cleanup routines
- Monitor memory usage and session count
- Consider implementing persistent storage for conversations
- Add authentication to sessions
- Implement conversation search functionality

---

For more information, see the main [README.md](README.md) file.
