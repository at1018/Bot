@echo off
REM Chatbot API Startup Script for Windows

echo 🤖 Starting Chatbot API...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found! Creating from .env.example...
    copy .env.example .env
    echo Please edit .env and add your OpenAI API key
    echo.
)

REM Start the application
echo.
echo 🚀 Starting FastAPI server...
echo 📚 API Documentation: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/api/health
echo.

python main.py

pause
