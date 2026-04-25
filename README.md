# Chatbot API

A powerful chatbot API built with FastAPI, LangChain, and OpenAI that can answer any question.

## Features

- 🤖 **LangChain Integration**: Leverages LangChain for advanced LLM interactions
- 🚀 **FastAPI**: Modern, fast web framework for building APIs
- 🔌 **OpenAI Integration**: Uses OpenAI's GPT models for intelligent responses
- � **Conversation History**: Maintains chat history for context-aware responses
- 🔄 **Session Management**: Support for multiple conversation sessions
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring
- 🔐 **CORS Support**: Cross-origin resource sharing enabled
- 📊 **Health Checks**: Built-in health check and model info endpoints
- 🎯 **Context Support**: Can provide context for more accurate answers
- 🧠 **Smart Context Awareness**: Uses previous conversations for better answers

## Project Structure

```
Bot/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── llm.py              # LLM configuration and chain
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py             # Pydantic models for request/response
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py           # Logging configuration
│   └── __init__.py
├── config/
│   ├── settings.py             # Application settings
├── logs/                        # Application logs
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                # Example environment variables
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or poetry
- OpenAI API key

### Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd Bot
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_api_key_here
   ```

## Configuration

Edit the `.env` file to configure the application:

```env
# FastAPI Configuration
API_TITLE=Chatbot API
API_VERSION=1.0.0
DEBUG=True

# LangChain Configuration
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Configuration Parameters

- **OPENAI_API_KEY**: Your OpenAI API key (required)
- **MODEL_NAME**: The OpenAI model to use (default: gpt-3.5-turbo)
- **TEMPERATURE**: Controls response randomness (0-1, default: 0.7)
- **DEBUG**: Enable debug mode (default: False)
- **PORT**: API port (default: 8000)
- **LOG_LEVEL**: Logging level (INFO, DEBUG, WARNING, ERROR)

## Running the Application

### Development Mode

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Chat Endpoint (with History Support)
**POST** `/api/chat`

Ask a question and get an answer with conversation history support.

**Request Body**:
```json
{
  "question": "What is artificial intelligence?",
  "context": "General knowledge",
  "session_id": "session_123"
}
```

**Response**:
```json
{
  "question": "What is artificial intelligence?",
  "answer": "Artificial intelligence (AI) is the simulation of human intelligence...",
  "model": "gpt-3.5-turbo",
  "session_id": "session_123",
  "timestamp": "2024-01-15T10:30:00",
  "history_used": true
}
```

**Features**:
- `session_id` is optional - if not provided, a new UUID is created
- `history_used` indicates if previous conversation context was used
- The chatbot uses last 5 messages for context-aware responses

### 2. Get Conversation History
**GET** `/api/history/{session_id}`

Retrieve the complete conversation history for a session.

**Response**:
```json
{
  "session_id": "session_123",
  "messages": [
    {
      "role": "human",
      "content": "What is Python?",
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "role": "assistant",
      "content": "Python is a high-level programming language...",
      "timestamp": "2024-01-15T10:30:05"
    }
  ],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:05",
  "message_count": 2
}
```

### 3. Get Session Info
**GET** `/api/session/{session_id}`

Get information about a specific session.

**Response**:
```json
{
  "session_id": "session_123",
  "message_count": 10,
  "created_at": "2024-01-15T10:30:00",
  "last_message_at": "2024-01-15T10:45:00"
}
```

### 4. List All Sessions
**GET** `/api/sessions`

Get a list of all active sessions.

**Response**:
```json
{
  "total_sessions": 3,
  "sessions": [
    {
      "session_id": "session_123",
      "message_count": 5,
      "created_at": "2024-01-15T10:30:00",
      "last_message_at": "2024-01-15T10:35:00"
    }
  ]
}
```

### 5. Clear Session History
**DELETE** `/api/history/{session_id}`

Clear all messages from a session while keeping the session active.

**Response**:
```json
{
  "session_id": "session_123",
  "status": "success",
  "message": "Conversation history cleared for session session_123"
}
```

### 6. Delete Session
**DELETE** `/api/session/{session_id}`

Delete a session completely.

**Response**:
```json
{
  "session_id": "session_123",
  "status": "success",
  "message": "Session session_123 deleted completely"
}
```

### 7. Health Check
**GET** `/api/health`

Check if the API is running.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 8. Model Information
**GET** `/api/info`

Get information about the current model configuration.

**Response**:
```json
{
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### 9. Root Endpoint
**GET** `/`

Get API information and available endpoints.

## Interactive Documentation

The API provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Examples

### Simple Chat (Without History)

Using cURL:
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

### Chat with Conversation History

Using Python with session management:
```python
import requests
import uuid

# Create a session
session_id = str(uuid.uuid4())

# Ask first question
response = requests.post("http://localhost:8000/api/chat", json={
    "question": "What is Python?",
    "session_id": session_id
})
print(response.json()['answer'])

# Ask follow-up question (will use history)
response = requests.post("http://localhost:8000/api/chat", json={
    "question": "What are its main advantages?",
    "session_id": session_id  # Same session for history
})
print(response.json()['answer'])
print(f"History used: {response.json()['history_used']}")
```

### Retrieve Conversation History

Using cURL:
```bash
curl "http://localhost:8000/api/history/{session_id}"
```

Using Python:
```python
import requests

session_id = "your_session_id"
response = requests.get(f"http://localhost:8000/api/history/{session_id}")
history = response.json()

for message in history['messages']:
    print(f"{message['role'].upper()}: {message['content']}")
```

### View Session Information

Using cURL:
```bash
curl "http://localhost:8000/api/session/{session_id}"
```

Using Python:
```python
import requests

session_id = "your_session_id"
info = requests.get(f"http://localhost:8000/api/session/{session_id}").json()
print(f"Messages in session: {info['message_count']}")
print(f"Created: {info['created_at']}")
print(f"Last message: {info['last_message_at']}")
```

### List All Active Sessions

```bash
curl "http://localhost:8000/api/sessions"
```

### JavaScript/Fetch with History

```javascript
const sessionId = generateUUID();

async function chat(question) {
    const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            question: question,
            session_id: sessionId
        })
    });
    return response.json();
}

async function getHistory() {
    const response = await fetch(`http://localhost:8000/api/history/${sessionId}`);
    return response.json();
}

// Ask questions
await chat("What is cloud computing?");
await chat("What are its benefits?");  // Will consider previous context

// Get conversation history
const history = await getHistory();
console.log(history.messages);
```

## Logging

Logs are stored in the `logs/` directory with a daily file naming convention:
- `logs/chatbot_YYYYMMDD.log`

Logs include:
- API requests and responses
- LLM interactions
- Errors and exceptions
- Application lifecycle events

## Conversation History & Session Management

### How It Works

The chatbot maintains conversation history for each session, allowing it to provide context-aware responses to follow-up questions.

**Key Features**:
- **Session-based**: Each conversation has a unique session ID
- **Context-aware**: Uses last 5 messages for context
- **Persistent**: History is maintained throughout the session
- **Manageable**: Can clear or delete session history
- **Trackable**: View session information and message count

### How Context Awareness Works

1. **First Question**: User asks "What is Python?"
   - No previous history
   - `history_used: false`

2. **Follow-up Question**: User asks "What are its main advantages?"
   - Bot considers the previous question and answer
   - Bot provides a more contextual response
   - `history_used: true`

3. **Related Question**: User asks "How do I get started?"
   - Bot considers the full conversation context
   - Bot provides installation/setup guidance based on Python context
   - `history_used: true`

### Session Management

```python
import requests
import uuid

# Start a new session
session_id = str(uuid.uuid4())

# Chat messages are automatically stored
requests.post("http://localhost:8000/api/chat", json={
    "question": "What is AI?",
    "session_id": session_id
})

# View all active sessions
sessions = requests.get("http://localhost:8000/api/sessions").json()

# Get session details
info = requests.get(f"http://localhost:8000/api/session/{session_id}").json()

# Retrieve conversation history
history = requests.get(f"http://localhost:8000/api/history/{session_id}").json()

# Clear history but keep session
requests.delete(f"http://localhost:8000/api/history/{session_id}")

# Delete entire session
requests.delete(f"http://localhost:8000/api/session/{session_id}")
```

## Error Handling

The API handles various error scenarios:

- **400 Bad Request**: Empty or invalid question
- **500 Internal Server Error**: LLM processing error
- **503 Service Unavailable**: Service not healthy

## Best Practices

1. **API Key Security**: Never commit your `.env` file with real API keys
2. **Rate Limiting**: Consider implementing rate limiting in production
3. **Temperature Setting**: 
   - Lower (0.3-0.5): More deterministic
   - Higher (0.7-1.0): More creative
4. **Context**: Provide relevant context for better answers
5. **Monitoring**: Monitor logs and API metrics in production

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution**: Check that your `.env` file exists and contains a valid OpenAI API key.

### Issue: "Connection refused" when accessing API
**Solution**: Ensure the server is running and you're using the correct host/port.

### Issue: Slow responses
**Solution**: 
- Check your internet connection
- Consider using a faster model like gpt-3.5-turbo
- Reduce the max_tokens value

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **LangChain**: LLM orchestration framework
- **LangChain-OpenAI**: OpenAI integration for LangChain
- **Pydantic**: Data validation
- **Python-dotenv**: Environment variable management

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue in the repository.

## Roadmap

- [ ] Add conversation history storage (Database support)
- [ ] Implement caching for frequently asked questions
- [ ] Add support for multiple LLM providers
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Deploy to cloud (AWS, Azure, GCP)
- [ ] Add WebSocket support for real-time chat
- [ ] Implement conversation export (JSON, PDF)
- [ ] Add conversation search functionality
- [ ] Implement conversation analytics and metrics

---

Happy chatting! 🤖
