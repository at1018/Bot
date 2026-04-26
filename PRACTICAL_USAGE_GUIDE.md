# Practical Usage Guide - Intelligent Query Detection System

## Quick Start

The system now automatically detects query types and applies appropriate formatting. **No code changes needed** - it works across all providers!

---

## Usage Examples

### Example 1: Code Request (Automatic Detection)

```bash
# Request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write a Python function to check if a number is prime"
  }'

# What Happens Behind the Scenes:
# 1. Question detected: "python" keyword found ✓
# 2. _is_code_request() returns True
# 3. CODE_SYSTEM_PROMPT injected (strict code rules)
# 4. LLM generates response with triple backticks
# 5. _format_code_response() preserves formatting
# 6. User receives properly formatted code

# Expected Response:
{
  "question": "Write a Python function to check if a number is prime",
  "answer": "```python\ndef is_prime(n):\n    \"\"\"Check if a number is prime.\"\"\"\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprint(is_prime(17))  # True\n```\n\n## Explanation\nThis function checks if a number is prime by testing divisibility from 2 to √n.\n\n## How to Run\n1. Copy the code into a .py file\n2. Run with `python your_file.py`\n3. Call `is_prime(number)` with any positive integer",
  "model": "gpt-3.5-turbo",
  "session_id": "...",
  "timestamp": "2026-04-26T...",
  "history_used": false
}
```

---

### Example 2: Code Request (JavaScript)

```bash
# Request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create a function to reverse a string in JavaScript"
  }'

# What Happens:
# 1. Keywords "function" and "javascript" detected ✓
# 2. CODE_SYSTEM_PROMPT applied
# 3. LLM generates JavaScript code
# 4. Response includes triple backticks

# Expected Response:
{
  "answer": "```javascript\nfunction reverseString(str) {\n  return str.split('').reverse().join('');\n}\n\nconsole.log(reverseString('hello'));  // 'olleh'\n```\n\n## Explanation\nSplits the string into an array, reverses it, and joins back together.\n\n## How to Run\n1. Save in a .js file\n2. Run with `node your_file.js`"
}
```

---

### Example 3: Text Request (Normal Question)

```bash
# Request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is REST API and how does it work?"
  }'

# What Happens:
# 1. No code keywords detected
# 2. _is_code_request() returns False
# 3. TEXT_SYSTEM_PROMPT injected (markdown structure)
# 4. LLM generates structured response
# 5. No code blocks in response

# Expected Response:
{
  "answer": "## What is REST API?\n\nREST (Representational State Transfer) is an architectural style for designing web services. It uses standard HTTP methods to perform operations on resources.\n\n## Key Principles\n\n- **Stateless**: Each request contains all information needed\n- **Client-Server**: Clear separation of concerns\n- **Cacheable**: Responses can be cached for performance\n- **Uniform Interface**: Consistent resource identification\n\n## How It Works\n\nREST APIs use standard HTTP methods:\n- **GET**: Retrieve data\n- **POST**: Create new resource\n- **PUT**: Update existing resource\n- **DELETE**: Remove resource\n\n## Example\n\nTo get a user with ID 123:\n```\nGET /api/users/123\n```\n\nTo create a new user:\n```\nPOST /api/users\nBody: { \"name\": \"John\", \"email\": \"john@example.com\" }\n```\n\n## Benefits\n\n- Simple and intuitive\n- Works with existing HTTP infrastructure\n- Scalable across many services\n- Language-agnostic"
}
```

---

### Example 4: Code with Explanation Request

```bash
# Request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me a Python example of list comprehension with explanation"
  }'

# What Happens:
# 1. Keywords "python" and "example" detected ✓
# 2. CODE_SYSTEM_PROMPT applied
# 3. LLM generates: code + explanation + usage

# Expected Response:
{
  "answer": "```python\n# Regular approach\nsquares = []\nfor i in range(1, 6):\n    squares.append(i ** 2)\n\n# List comprehension (cleaner)\nsquares = [i ** 2 for i in range(1, 6)]\n\nprint(squares)  # [1, 4, 9, 16, 25]\n```\n\n## Explanation\n\nList comprehension provides a concise way to create lists. Instead of using a loop, you write the operation in a single line within brackets.\n\n## Syntax\n\n```\n[expression for item in iterable if condition]\n```\n\n## How to Run\n\n1. Save the code in a .py file\n2. Run: `python your_file.py`\n3. Output: `[1, 4, 9, 16, 25]`\n\n## More Examples\n\n- Filter even numbers: `[x for x in range(10) if x % 2 == 0]`\n- Convert to uppercase: `[name.upper() for name in names]`\n- Nested comprehension: `[[x*y for y in range(3)] for x in range(3)]`"
}
```

---

## Provider-Specific Tests

### Test with Gemini Provider

```python
# Set environment
export GOOGLE_API_KEY="your_key"
export LLM_PROVIDER="gemini"

# Request code
curl -X POST http://localhost:8000/api/chat \
  -d '{"question": "Write Python code for factorial"}'

# Result: ✅ CODE_SYSTEM_PROMPT applied, response in backticks
```

### Test with Anthropic Provider

```python
# Set environment
export ANTHROPIC_API_KEY="your_key"
export LLM_PROVIDER="anthropic"

# Request explanation
curl -X POST http://localhost:8000/api/chat \
  -d '{"question": "Explain decorators in Python"}'

# Result: ✅ TEXT_SYSTEM_PROMPT applied, structured markdown
```

### Test with OpenAI Provider

```python
# Set environment
export OPENAI_API_KEY="your_key"
export LLM_PROVIDER="openai"

# Mixed request
curl -X POST http://localhost:8000/api/chat \
  -d '{"question": "How do decorators work? Give an example"}'

# Result: ✅ CODE_SYSTEM_PROMPT applied (keyword "example")
```

### Test with Groq Provider

```python
# Set environment
export GROQ_API_KEY="your_key"
export LLM_PROVIDER="groq"

# Code request
curl -X POST http://localhost:8000/api/chat \
  -d '{"question": "Create a REST API endpoint using Flask"}'

# Result: ✅ CODE_SYSTEM_PROMPT applied (keywords: "API", "Flask")
```

---

## Keyword Matching Examples

### Keywords That Trigger CODE_SYSTEM_PROMPT

```
✅ "Write Python code for..."
✅ "Create a JavaScript function..."
✅ "Build a REST API..."
✅ "Implement algorithm for..."
✅ "Generate regex pattern..."
✅ "Fix this bug in Java..."
✅ "Debug this code snippet..."
✅ "Refactor this function..."
✅ "Develop a Flask application..."
✅ "Build a React component..."
✅ "Query a database..."
✅ "Class definition example..."
✅ "Method implementation..."
✅ "Code template for..."
```

### Keywords That Trigger TEXT_SYSTEM_PROMPT

```
✅ "What is REST API?"
✅ "Explain machine learning"
✅ "How does JavaScript work?"
✅ "Compare Python and Java"
✅ "Tell me about microservices"
✅ "What are design patterns?"
✅ "Define asynchronous programming"
✅ "List the benefits of..."
✅ "Describe the process of..."
✅ "Why should I use..."
```

---

## Conversation with History

```bash
# Request 1: Code request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write Python code for bubble sort",
    "session_id": "session-123"
  }'

# Response includes code with backticks ✅

# Request 2: Follow-up with history
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain how the sorting works",
    "session_id": "session-123"
  }'

# Backend:
# 1. Retrieves conversation history
# 2. Detects "Explain how" - NOT a code request
# 3. TEXT_SYSTEM_PROMPT applied ✅
# 4. Response includes context from previous code
# 5. Returns structured explanation

# Result: Markdown formatted explanation that references the bubble sort code
```

---

## Extraction Levels

```bash
# Level 1: Minimal (default)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain Python",
    "session_id": "s1"
  }'
# Response: Brief, concise answer

# Level 2: Medium (with context)
curl -X PUT http://localhost:8000/api/extraction-level \
  -d '{"level": 2}'

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain Python",
    "session_id": "s1"
  }'
# Response: Detailed with examples and context

# Level 3: Detailed (comprehensive)
curl -X PUT http://localhost:8000/api/extraction-level \
  -d '{"level": 3}'

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain Python",
    "session_id": "s1"
  }'
# Response: Comprehensive analysis with deep context
```

---

## API Endpoints Reference

```bash
# Get current model info
curl http://localhost:8000/api/info

# Get current extraction level
curl http://localhost:8000/api/extraction-level

# Set extraction level (1-3)
curl -X PUT http://localhost:8000/api/extraction-level \
  -H "Content-Type: application/json" \
  -d '{"level": 2}'

# Health check
curl http://localhost:8000/api/health

# Chat (main endpoint)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Your question here",
    "context": "Optional context",
    "session_id": "Optional session ID"
  }'

# Get conversation history
curl "http://localhost:8000/api/history?session_id=session-123"

# Clear history
curl -X DELETE "http://localhost:8000/api/history?session_id=session-123"
```

---

## Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

class ChatbotClient:
    def __init__(self, session_id=None):
        self.session_id = session_id
        self.BASE_URL = BASE_URL
    
    def ask(self, question, context=None):
        """Ask a question (auto-detects code vs text)"""
        payload = {
            "question": question,
            "session_id": self.session_id
        }
        if context:
            payload["context"] = context
        
        response = requests.post(
            f"{self.BASE_URL}/chat",
            json=payload
        )
        return response.json()
    
    def set_extraction_level(self, level):
        """Set extraction level (1-3)"""
        response = requests.put(
            f"{self.BASE_URL}/extraction-level",
            json={"level": level}
        )
        return response.json()
    
    def get_model_info(self):
        """Get current model info"""
        response = requests.get(f"{self.BASE_URL}/info")
        return response.json()

# Usage
client = ChatbotClient(session_id="my_session")

# Code request (auto-detected)
response = client.ask("Write Python code for fibonacci")
print(response["answer"])
# Output: Properly formatted code with backticks ✅

# Text request (auto-detected)
response = client.ask("What is Python?")
print(response["answer"])
# Output: Structured markdown text ✅

# Set extraction level
client.set_extraction_level(2)
response = client.ask("Explain OOP")
# Response will be more detailed
```

---

## Testing Checklist

Use this checklist to verify the system is working correctly:

```
✅ CODE REQUEST TESTS
──────────────────────────────────────────
□ "Write Python code for..." → Code in backticks ✓
□ "Create JavaScript function" → Code in backticks ✓
□ "Build REST API" → Code in backticks ✓
□ "Generate SQL query" → Code in backticks ✓
□ "Implement algorithm" → Code in backticks ✓
□ Indentation is correct ✓
□ Language identifier present (```python, etc) ✓
□ Includes "## Explanation" section ✓
□ Includes "## How to Run" section ✓

✅ TEXT REQUEST TESTS
──────────────────────────────────────────
□ "What is Python?" → Structured markdown ✓
□ "Explain REST API" → Headers (##, ###) ✓
□ "Compare X and Y" → Bullet points ✓
□ "Tell me about..." → **Bold** terms ✓
□ No unnecessary code blocks ✓
□ Clear organization ✓
□ Professional tone ✓

✅ PROVIDER TESTS
──────────────────────────────────────────
□ Gemini: Code request → backticks ✓
□ Anthropic: Text request → markdown ✓
□ OpenAI: Mixed request → correct detection ✓
□ Groq: Code request → backticks ✓

✅ SPECIAL CASES
──────────────────────────────────────────
□ Mixed query (code + explanation) → CODE prompt ✓
□ No keywords detected → TEXT prompt ✓
□ With conversation history → Maintains context ✓
□ Extraction level 1 → Concise ✓
□ Extraction level 2 → Detailed ✓
□ Extraction level 3 → Comprehensive ✓
```

---

## Troubleshooting

### Issue: Text response contains code blocks

**Cause**: Keyword detection triggered CODE_SYSTEM_PROMPT when TEXT was intended

**Solution**: Ask more clearly:
```
❌ "How to code a function?"
✅ "How can I write a function?"
```

### Issue: Code response doesn't have backticks

**Cause**: Model ignored instruction or response went to `_format_code_response` unformatted

**Solution**: The `_format_code_response()` method should auto-wrap it. If not:
- Check LLM provider is working
- Verify system prompt was injected
- Check response for formatting issues

### Issue: All responses formatted wrong

**Cause**: Chain not initialized correctly

**Solution**:
```python
# Make sure setup_chain() is called during __init__
class MyProvider(BaseLLMProvider):
    def initialize(self):
        # ... initialize llm ...
        self.setup_chain()  # ✅ Critical!
```

---

This practical guide should help you use and test the intelligent query detection system! 🚀
