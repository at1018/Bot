# QUICK START - 5 Minute Setup

## TL;DR - Just Run These Commands

### Terminal 1: Start Backend

```powershell
cd "c:\Users\anujt\OneDrive\Documents\Bot"
venv\Scripts\activate
python main.py
```

✅ Wait for: `Uvicorn running on http://127.0.0.1:8000`

### Terminal 2: Start Frontend

```powershell
cd "c:\Users\anujt\OneDrive\Documents\Bot\frontend"
npm start
```

✅ Browser opens at http://localhost:3000

### Start Chatting! 🚀

Visit: http://localhost:3000

---

## Prerequisites (One-Time Setup)

### 1. Add Your OpenAI API Key

```powershell
notepad "c:\Users\anujt\OneDrive\Documents\Bot\.env"
```

Replace `your_openai_api_key_here` with your actual key:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save and close (Ctrl+S, Alt+F4)

### 2. Install Frontend Dependencies (First Time Only)

```powershell
cd "c:\Users\anujt\OneDrive\Documents\Bot\frontend"
npm install
```

---

## URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Chatbot UI |
| Backend | http://localhost:8000 | API Server |
| API Docs | http://localhost:8000/docs | Interactive API |
| Health Check | http://localhost:8000/api/health | API Status |
| Redoc | http://localhost:8000/redoc | API Documentation |

---

## Folder Structure You Need to Know

```
Bot/
├── main.py                    ← Backend (Run: python main.py)
├── .env                       ← Your API key here
└── frontend/
    └── package.json           ← Frontend (Run: npm start)
```

---

## If Something Goes Wrong

| Error | Fix |
|-------|-----|
| API not responding | Restart backend: `python main.py` |
| No messages | Check API key in .env |
| npm not found | Install Node.js from nodejs.org |
| Port 8000 in use | Kill process or use port 8001 |
| Messages empty | Open DevTools (F12), check Console |

---

## Architecture (High Level)

```
React Frontend (3000)
        ↓ HTTP API calls
FastAPI Backend (8000)
        ↓ LLM calls
OpenAI API
        ↓ Returns response
Backend stores in memory
        ↓
Frontend displays message
```

---

## Testing

### Test 1: API Health
```
Visit: http://localhost:8000/api/health
Expected: {"status": "healthy", "version": "1.0.0"}
```

### Test 2: Send Message
```
Visit: http://localhost:3000
Type: "What is AI?"
Expected: Bot responds with answer
```

### Test 3: Context Awareness
```
Message 1: "What is Python?"
Message 2: "What are its advantages?"
Expected: Bot mentions Python in advantages
```

---

## Key Features

✨ **Works Now:**
- ✅ Chat with AI
- ✅ Conversation history (same session)
- ✅ Context awareness (remembers previous messages)
- ✅ Session management
- ✅ Beautiful modern UI
- ✅ Responsive mobile design

---

## File Checklist

Your project should have these files:

```
Bot/
├── main.py ✓
├── requirements.txt ✓
├── .env (with your API key) ✓
├── app/
│   ├── api/routes.py ✓
│   ├── core/llm.py ✓
│   ├── core/memory.py ✓
│   └── ...
├── frontend/
│   ├── package.json ✓
│   ├── src/App.js ✓
│   ├── src/components/ ✓
│   └── ...
├── ARCHITECTURE.md ✓
├── SETUP_GUIDE.md ✓
└── CONVERSATION_HISTORY.md ✓
```

---

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-xxxx         # Required!
MODEL_NAME=gpt-3.5-turbo       # Optional
TEMPERATURE=0.7                # Optional
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000  # Should be correct
```

---

## Useful Terminal Commands

### Backend
```powershell
# Start backend
python main.py

# Stop backend
Ctrl + C

# Reinstall dependencies
pip install -r requirements.txt

# Activate virtual environment
venv\Scripts\activate

# Deactivate virtual environment
deactivate
```

### Frontend
```powershell
# Start frontend
npm start

# Stop frontend
Ctrl + C

# Reinstall dependencies
npm install

# Build for production
npm run build
```

---

## Component Overview

```
Frontend Structure:
├── App.js (Main)
│   ├── Sidebar (Info + Navigation)
│   └── ChatContainer
│       ├── ChatWindow (Messages)
│       └── InputArea (Input + Buttons)
│
Backend Structure:
├── main.py (FastAPI app)
│   ├── routes.py (API endpoints)
│   ├── llm.py (LLM logic)
│   └── memory.py (Session storage)
```

---

## State Management

**What Gets Stored:**
- Current session ID
- Messages in this session
- Loading state
- Error messages
- Model information

**Where It's Stored:**
- React Context (in-memory)
- LocalStorage (session persistence)
- Backend Memory (conversation history)

---

## API Endpoints

```
POST   /api/chat                  Send message
GET    /api/history/{id}          Get chat history
GET    /api/session/{id}          Get session info
GET    /api/sessions              List all sessions
DELETE /api/history/{id}          Clear history
GET    /api/health                Health check
GET    /api/info                  Model info
```

---

## Performance Tips

- First load takes 5-10 seconds (LLM model loading)
- Subsequent messages are faster
- Longer responses take longer
- Use shorter questions for faster responses

---

## What's Happening Behind the Scenes

```
You: "What is Python?"
↓
Frontend sends HTTP POST to backend
↓
Backend receives request with session ID
↓
Backend retrieves previous messages from memory
↓
Backend creates LLM prompt with context
↓
Backend calls OpenAI API
↓
OpenAI returns response
↓
Backend stores messages in memory
↓
Backend sends response to frontend
↓
Frontend displays message
↓
UI updates automatically
```

---

## Next: Advanced Features

Once you have it running, check out:
- 📖 **ARCHITECTURE.md** - How everything works
- 📖 **CONVERSATION_HISTORY.md** - Advanced session management
- 📚 **Customize components** - Make it your own
- 🚀 **Deploy** - Put it on the cloud

---

## Quick Links

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **OpenAI API**: https://platform.openai.com/
- **LangChain**: https://python.langchain.com/

---

## Still Stuck?

1. **Check this file first** ← You're reading it!
2. **Read SETUP_GUIDE.md** - More detailed instructions
3. **Read ARCHITECTURE.md** - Understand how it works
4. **Check terminal for error messages** - They usually tell you what's wrong
5. **Open DevTools (F12)** - Check browser console for errors

---

**You're all set!** 🎉

Run the commands in Terminal 1 and Terminal 2, then visit http://localhost:3000

Enjoy your AI chatbot! 🚀

