# Complete Setup Guide - Running Backend & Frontend

## Prerequisites

### System Requirements
- **Python** 3.8+ (for backend)
- **Node.js** 14+ & npm (for frontend)
- **Git** (optional, for version control)
- **OpenAI API Key** (https://platform.openai.com/api-keys)

### Verify Installation

```powershell
# Check Python
python --version

# Check Node.js
node --version
npm --version
```

---

## Step 1: Backend Setup (FastAPI)

### 1.1 Navigate to Bot Directory

```powershell
cd "c:\Users\anujt\OneDrive\Documents\Bot"
```

### 1.2 Create Virtual Environment

```powershell
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate
```

You should see `(venv)` prefix in terminal:
```
(venv) C:\Users\anujt\OneDrive\Documents\Bot>
```

### 1.3 Install Backend Dependencies

```powershell
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi uvicorn langchain langchain-openai ...
```

### 1.4 Configure Environment Variables

```powershell
# Copy example file
copy .env.example .env

# Open .env in notepad
notepad .env
```

Edit `.env` and replace with your OpenAI API key:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
HOST=0.0.0.0
PORT=8000
```

**Get API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy and paste in .env

### 1.5 Run Backend Server

```powershell
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Keep this terminal open!** ← Important

### 1.6 Verify Backend is Running

Open your browser and visit:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **Model Info:** http://localhost:8000/api/info

---

## Step 2: Frontend Setup (React)

### 2.1 Open New PowerShell Terminal

**Do not close the backend terminal!** Open a new one:

```powershell
# New Terminal - Navigate to frontend
cd "c:\Users\anujt\OneDrive\Documents\Bot\frontend"
```

### 2.2 Install Frontend Dependencies

```powershell
npm install
```

**First time only** - This will take 2-3 minutes.

Expected output:
```
added 1234 packages in 45s
```

### 2.3 Configure Frontend Environment

```powershell
# Copy example file
copy .env.example .env

# Edit .env (optional - already configured for localhost:8000)
notepad .env
```

**Default is:**
```
REACT_APP_API_URL=http://localhost:8000
```

This is correct for local development.

### 2.4 Start Frontend Development Server

```powershell
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view chatbot-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
```

Your default browser should open automatically at `http://localhost:3000`

---

## Step 3: Test the Application

### 3.1 Open the Chatbot UI

If browser didn't open, manually visit: http://localhost:3000

### 3.2 Check Sidebar for Status

Look for in the sidebar:
- ✅ **Model Info** - Shows gpt-3.5-turbo (means API connected)
- ✅ **Session Info** - Shows message count
- ⚠️ **Error Banner** - If API not connected

### 3.3 Send Your First Message

1. Click on the message input field
2. Type: "What is artificial intelligence?"
3. Click Send button (or press Enter)
4. Wait for response...

### 3.4 Test Conversation History

1. Send: "What is artificial intelligence?"
2. Send follow-up: "What are its applications?"
3. Notice `history_used: true` indicates context awareness

---

## Terminal Setup Summary

You need **3 terminals** running:

```
Terminal 1: Backend (FastAPI)
├─ cd "c:\Users\anujt\OneDrive\Documents\Bot"
├─ venv\Scripts\activate
└─ python main.py
   → Running on http://localhost:8000

Terminal 2: Frontend (React)
├─ cd "c:\Users\anujt\OneDrive\Documents\Bot\frontend"
└─ npm start
   → Running on http://localhost:3000

Terminal 3: Optional (for other tasks)
└─ Available for testing, logs, etc.
```

---

## Quick Reference Commands

### Backend Commands

```powershell
# Navigate to project
cd "c:\Users\anujt\OneDrive\Documents\Bot"

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py

# Deactivate venv (when done)
deactivate
```

### Frontend Commands

```powershell
# Navigate to frontend
cd "c:\Users\anujt\OneDrive\Documents\Bot\frontend"

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Stop server
# Ctrl + C in terminal
```

---

## Testing Endpoints

### Using Browser

**Health Check:**
```
http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

**API Docs:**
```
http://localhost:8000/docs
```

Interactive API documentation with try-it-out feature.

### Using PowerShell (Curl)

```powershell
# Test health
curl http://localhost:8000/api/health

# Test chat
curl -X POST "http://localhost:8000/api/chat" `
  -H "Content-Type: application/json" `
  -d '{
    "question": "What is Python?",
    "session_id": "test-123"
  }' | ConvertFrom-Json | Format-List
```

---

## Troubleshooting

### Issue: "API is not responding"

**Error in browser:** "No response from server. Is the API running?"

**Solution:**
1. Check if backend terminal is still running
2. Look for error messages in backend terminal
3. Verify OPENAI_API_KEY is set correctly
4. Check http://localhost:8000/api/health

```powershell
# Restart backend
python main.py
```

### Issue: "ModuleNotFoundError" in Backend

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```powershell
# Make sure venv is activated (should see (venv) prefix)
# Install dependencies again
pip install -r requirements.txt
```

### Issue: "npm command not found"

**Error:** `npm: The term 'npm' is not recognized`

**Solution:**
1. Install Node.js from https://nodejs.org/
2. Restart PowerShell
3. Verify: `npm --version`

### Issue: "Port 8000 already in use"

**Error:** `Address already in use`

**Solution:**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

### Issue: Frontend shows empty chat

**Problem:** Messages aren't loading

**Solution:**
1. Open browser DevTools (F12)
2. Check Console for errors
3. Check Network tab for API calls
4. Verify REACT_APP_API_URL in .env

```powershell
# Restart frontend
npm start
```

### Issue: "OPENAI_API_KEY not found"

**Error:** ValueError: OPENAI_API_KEY environment variable not set

**Solution:**
1. Check .env file exists
2. Verify OPENAI_API_KEY line is present
3. Make sure no typos in key
4. Restart backend after editing .env

```powershell
# View .env
type .env

# Should show:
# OPENAI_API_KEY=sk-...
```

---

## File Locations

### Key Files to Know

**Backend:**
```
Bot\
├── main.py              ← Run this to start backend
├── .env                 ← Your API key here
├── requirements.txt     ← Dependencies
└── app\
    ├── api\routes.py   ← Endpoints
    ├── core\llm.py     ← LLM logic
    └── core\memory.py  ← Session storage
```

**Frontend:**
```
frontend\
├── package.json         ← Dependencies
├── .env                 ← API URL
├── README.md            ← Frontend docs
└── src\
    ├── App.js          ← Main component
    ├── context\        ← State management
    ├── components\     ← UI components
    └── services\       ← API calls
```

**Logs:**
```
Bot\logs\
└── chatbot_YYYYMMDD.log  ← Application logs
```

---

## Project Structure at a Glance

```
Bot/                                    ← Main Project
├── backend (Python/FastAPI)
│   ├── main.py                        ← Start here: python main.py
│   ├── app/                           ← Application code
│   ├── config/                        ← Settings
│   ├── .env                           ← API Key
│   └── requirements.txt               ← Dependencies
│
├── frontend (React)                   ← Start here: npm start
│   ├── package.json                   ← npm dependencies
│   ├── src/                           ← React code
│   ├── public/                        ← Static files
│   ├── .env                           ← API URL
│   └── README.md                      ← Frontend docs
│
├── README.md                          ← Main docs
├── ARCHITECTURE.md                    ← How it works
├── CONVERSATION_HISTORY.md            ← History features
└── setup_guide.md                     ← This file
```

---

## Development Workflow

### For Backend Development

```powershell
# 1. Terminal 1 - Start backend
cd "c:\Users\anujt\OneDrive\Documents\Bot"
venv\Scripts\activate
python main.py

# 2. Make changes to Python files
# 3. Server auto-restarts (with --reload flag)
# 4. Test via http://localhost:8000/docs
```

### For Frontend Development

```powershell
# 1. Terminal 2 - Start frontend
cd "c:\Users\anujt\OneDrive\Documents\Bot\frontend"
npm start

# 2. Make changes to React files
# 3. Browser auto-refreshes
# 4. Hot Module Replacement (HMR) in action
```

### Testing

```powershell
# Terminal 3 - Run tests or commands
cd "c:\Users\anujt\OneDrive\Documents\Bot\frontend"
npm test

# Or run example script
cd "c:\Users\anujt\OneDrive\Documents\Bot"
python example_usage.py
```

---

## Deployment Checklist

- [ ] Backend running on correct port (8000)
- [ ] Frontend running on correct port (3000)
- [ ] API Key configured in .env
- [ ] CORS enabled for frontend URL
- [ ] Health check passing
- [ ] Message sending works
- [ ] Conversation history loads
- [ ] No errors in console/terminal

---

## Next Steps

1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:3000
3. ✅ Can send messages and get responses
4. 📖 Read ARCHITECTURE.md for deeper understanding
5. 📖 Read CONVERSATION_HISTORY.md for advanced features
6. 🚀 Customize and extend as needed

---

## Tips & Tricks

### Save Bandwidth During Development
```powershell
# Don't rebuild on every file save
npm start -- --no-cache
```

### View Logs in Real-time
```powershell
# In new terminal
tail -f logs/chatbot_*.log
```

### Test API Without Frontend
```powershell
# Open interactive docs
http://localhost:8000/docs

# Or use curl/Postman
curl -X POST http://localhost:8000/api/chat ...
```

### Debug Mode
Edit `.env`:
```
DEBUG=True
LOG_LEVEL=DEBUG
```

---

## Support & Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **LangChain Docs:** https://python.langchain.com/
- **OpenAI Docs:** https://platform.openai.com/docs/

---

**Ready? Let's start!** 🚀

1. Open first terminal → Start backend
2. Open second terminal → Start frontend
3. Visit http://localhost:3000
4. Start chatting!
