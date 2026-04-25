"""
Example usage of the Chatbot API with conversation history support.
Run this after starting the FastAPI server.
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8000"


def chat(question: str, session_id: str, context: str = None) -> dict:
    """
    Send a question to the chatbot API and get an answer.
    
    Args:
        question: The question to ask
        session_id: Session ID for conversation history
        context: Optional context for the question
        
    Returns:
        The API response
    """
    payload = {
        "question": question,
        "context": context,
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Is it running?")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.status_code} - {e.response.text}")
        return None


def get_conversation_history(session_id: str) -> dict:
    """Get conversation history for a session."""
    try:
        response = requests.get(f"{BASE_URL}/api/history/{session_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"No history found for session {session_id}")
        else:
            print(f"Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error getting history: {e}")
        return None


def get_session_info(session_id: str) -> dict:
    """Get session information."""
    try:
        response = requests.get(f"{BASE_URL}/api/session/{session_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting session info: {e}")
        return None


def list_sessions() -> dict:
    """List all active sessions."""
    try:
        response = requests.get(f"{BASE_URL}/api/sessions")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error listing sessions: {e}")
        return None


def clear_history(session_id: str) -> dict:
    """Clear conversation history for a session."""
    try:
        response = requests.delete(f"{BASE_URL}/api/history/{session_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error clearing history: {e}")
        return None


def delete_session(session_id: str) -> dict:
    """Delete a session."""
    try:
        response = requests.delete(f"{BASE_URL}/api/session/{session_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error deleting session: {e}")
        return None


def health_check() -> dict:
    """Check if the API is healthy."""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Health check failed: {e}")
        return None


def get_model_info() -> dict:
    """Get model information."""
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to get model info: {e}")
        return None


def main():
    """Main function demonstrating conversation history."""
    
    print("=" * 70)
    print("Chatbot API - Example with Conversation History Support")
    print("=" * 70)
    print()
    
    # Check health
    print("1️⃣  Checking API health...")
    health = health_check()
    if not health:
        print("❌ API is not responding. Please start it first.")
        return
    print(f"✅ Status: {health['status']}")
    print(f"   Version: {health['version']}")
    print()
    
    # Get model info
    print("2️⃣  Getting model information...")
    model_info = get_model_info()
    if model_info:
        print(f"✅ Model: {model_info['model']}")
        print(f"   Temperature: {model_info['temperature']}")
        print(f"   Max Tokens: {model_info['max_tokens']}")
    print()
    
    # Create a session for related questions
    session_id = str(uuid.uuid4())
    print("3️⃣  Demonstrating Conversation History")
    print(f"   Session ID: {session_id}")
    print()
    
    # Ask related questions in sequence
    print("4️⃣  Asking related questions in the same session...")
    print("-" * 70)
    
    questions = [
        "What is Python?",
        "What are its main advantages?",
        "How do I get started with it?",
        "What frameworks are popular?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print(f"Using session: {session_id}")
        print("Processing...")
        
        response = chat(question, session_id)
        
        if response:
            print(f"✅ Answer: {response['answer'][:200]}...")  # Show first 200 chars
            print(f"   History Used: {response['history_used']}")
            print(f"   Model: {response['model']}")
        
        print("-" * 70)
    
    # Display conversation history
    print("\n5️⃣  Retrieving Full Conversation History")
    print("-" * 70)
    history = get_conversation_history(session_id)
    
    if history:
        print(f"Session: {history['session_id']}")
        print(f"Total Messages: {history['message_count']}")
        print(f"Created: {history['created_at']}")
        print(f"Updated: {history['updated_at']}")
        print("\nConversation:")
        for i, msg in enumerate(history['messages'], 1):
            role = msg['role'].upper()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"  {i}. [{role}] {content}")
    print()
    
    # Display session info
    print("6️⃣  Session Information")
    print("-" * 70)
    session_info = get_session_info(session_id)
    if session_info:
        print(f"Session ID: {session_info['session_id']}")
        print(f"Message Count: {session_info['message_count']}")
        print(f"Created: {session_info['created_at']}")
        print(f"Last Message: {session_info['last_message_at']}")
    print()
    
    # List all sessions
    print("7️⃣  All Active Sessions")
    print("-" * 70)
    sessions = list_sessions()
    if sessions:
        print(f"Total Sessions: {sessions['total_sessions']}")
        for sess in sessions['sessions']:
            print(f"  - {sess['session_id']}: {sess['message_count']} messages")
    print()
    
    # Interactive mode
    print("=" * 70)
    print("8️⃣  Interactive Chat Mode (with History)")
    print("=" * 70)
    print("Features:")
    print("  • Type 'history' to see conversation history")
    print("  • Type 'new' to start a new session")
    print("  • Type 'info' to see session info")
    print("  • Type 'quit' to exit")
    print()
    
    current_session = session_id
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            print("👋 Goodbye!")
            break
        
        elif user_input.lower() == "history":
            history = get_conversation_history(current_session)
            if history:
                print(f"\n📜 Conversation History ({history['message_count']} messages):")
                for msg in history['messages']:
                    role = msg['role'].upper()
                    print(f"  [{role}] {msg['content'][:150]}")
            continue
        
        elif user_input.lower() == "new":
            current_session = str(uuid.uuid4())
            print(f"\n✅ New session created: {current_session}")
            continue
        
        elif user_input.lower() == "info":
            info = get_session_info(current_session)
            if info:
                print(f"\n📊 Session Info:")
                print(f"  ID: {info['session_id']}")
                print(f"  Messages: {info['message_count']}")
                print(f"  Created: {info['created_at']}")
            continue
        
        # Regular chat
        response = chat(user_input, current_session)
        if response:
            print(f"\n🤖 Bot: {response['answer']}")
            if response['history_used']:
                print("   [Using conversation history for context]")


if __name__ == "__main__":
    main()
