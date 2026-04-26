/**
 * MARKDOWN RENDERING TEST EXAMPLES
 * 
 * These are example markdown responses that your backend could send.
 * You can use these to test the markdown rendering in your chatbot UI.
 * 
 * How to use:
 * 1. Copy the markdown content from any example below
 * 2. Paste it directly as a bot response in your chat
 * 3. Verify that it renders correctly with formatting, code highlighting, etc.
 */

// ============================================
// Example 1: Python Code Block
// ============================================
export const EXAMPLE_1_PYTHON = `## How to Calculate Factorial

Here's a simple Python function to calculate factorial:

\`\`\`python
def factorial(n):
    """Calculate factorial of n recursively"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test the function
result = factorial(5)
print(f"Factorial of 5 is {result}")  # Output: 120
\`\`\`

**Key Points:**
- The function uses recursion
- Base case: n <= 1 returns 1
- Recursive case: n * factorial(n-1)

> **Note:** For large values of n, consider using iterative approach to avoid stack overflow.`;

// ============================================
// Example 2: JavaScript/React Code
// ============================================
export const EXAMPLE_2_JAVASCRIPT = `## React Hooks Example

Learn how to use \`useState\` hook for state management:

\`\`\`javascript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}

export default Counter;
\`\`\`

### How it works:

1. **useState(0)** - Initialize count to 0
2. **setCount** - Function to update count
3. **Click handler** - Increments count by 1

\`\`\`javascript
// You can also use multiple states:
const [name, setName] = useState('John');
const [age, setAge] = useState(25);
\`\`\``;

// ============================================
// Example 3: SQL Code Block
// ============================================
export const EXAMPLE_3_SQL = `## Database Query Example

Here's how to retrieve user data with filtering:

\`\`\`sql
SELECT 
    user_id,
    username,
    email,
    created_at
FROM users
WHERE 
    created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND status = 'active'
ORDER BY created_at DESC
LIMIT 10;
\`\`\`

### Query Explanation:

| Part | Purpose |
|------|---------|
| SELECT | Retrieve specific columns |
| FROM users | Table to query |
| WHERE | Filter conditions |
| ORDER BY | Sort results |
| LIMIT | Limit number of rows |

**Tips for optimization:**
- Always add WHERE clause to limit data
- Use LIMIT to prevent large result sets
- Create indexes on frequently filtered columns`;

// ============================================
// Example 4: JSON Configuration
// ============================================
export const EXAMPLE_4_JSON = `## API Configuration

Here's the JSON configuration for the API:

\`\`\`json
{
  "api": {
    "host": "api.example.com",
    "port": 8000,
    "version": "v1",
    "timeout": 30
  },
  "authentication": {
    "type": "bearer",
    "token": "your_token_here"
  },
  "database": {
    "host": "db.example.com",
    "port": 5432,
    "name": "myapp",
    "pool_size": 10
  }
}
\`\`\`

### Configuration options:

- **host**: API server hostname
- **port**: Port number (default: 8000)
- **version**: API version to use
- **timeout**: Request timeout in seconds`;

// ============================================
// Example 5: Mixed Markdown (Headings, Lists, Bold, Italic)
// ============================================
export const EXAMPLE_5_MIXED = `## Getting Started Guide

Welcome! This guide will help you get started with our service.

### Prerequisites

Before you begin, make sure you have:

- **Node.js** (version 14 or higher)
- **npm** or *yarn* package manager
- \`git\` command-line tool
- A text editor (VS Code recommended)

### Installation Steps

1. Clone the repository
2. Install dependencies using \`npm install\`
3. Configure environment variables
4. Run \`npm start\` to begin

### Important Files

- **\`.env\`** - Environment configuration
- **\`package.json\`** - Project dependencies
- **\`src/index.js\`** - Application entry point

> **Tip:** Always backup your configuration files before making changes!

### Common Commands

\`\`\`bash
npm install    # Install dependencies
npm start      # Start development server
npm run build  # Build for production
npm test       # Run tests
\`\`\``;

// ============================================
// Example 6: Complex Markdown with Code and Blockquote
// ============================================
export const EXAMPLE_6_COMPLEX = `## Understanding Async/Await

### What is Async/Await?

Async/await is a way to write **asynchronous** code that looks and behaves like synchronous code.

\`\`\`javascript
async function fetchUserData(userId) {
  try {
    const response = await fetch(\`/api/users/\${userId}\`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}
\`\`\`

### Key Concepts:

- **async function** - Declares an asynchronous function
- **await** - Pauses execution until Promise resolves
- **try/catch** - Error handling for async operations

> **Important:** Always use try/catch blocks with async/await to handle errors gracefully!

### Comparison

**Before (Promises):**
\`\`\`javascript
function fetchUser(id) {
  return fetch(\`/api/users/\${id}\`)
    .then(r => r.json())
    .catch(e => console.error(e));
}
\`\`\`

**After (Async/Await):**
\`\`\`javascript
async function fetchUser(id) {
  try {
    const r = await fetch(\`/api/users/\${id}\`);
    return await r.json();
  } catch (e) {
    console.error(e);
  }
}
\`\`\``;

// ============================================
// Example 7: Code Highlighting Test (Multiple Languages)
// ============================================
export const EXAMPLE_7_MULTICODE = `## Multiple Programming Languages

### Python

\`\`\`python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        print(f"Hello, I'm {self.name}")
\`\`\`

### Java

\`\`\`java
public class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public void greet() {
        System.out.println("Hello, I'm " + this.name);
    }
}
\`\`\`

### Go

\`\`\`go
package main

import "fmt"

type Person struct {
    Name string
    Age  int
}

func (p Person) Greet() {
    fmt.Printf("Hello, I'm %s\\n", p.Name)
}
\`\`\``;

// ============================================
// Example 8: Inline Code + Code Blocks
// ============================================
export const EXAMPLE_8_INLINE_CODE = `## Package Installation

To install the \`react-markdown\` package, use npm:

\`\`\`bash
npm install react-markdown
\`\`\`

Then import it in your component:

\`\`\`javascript
import ReactMarkdown from 'react-markdown';

export function App() {
  const markdown = "# Hello\\n\\nThis is **bold** text";
  return <ReactMarkdown>{markdown}</ReactMarkdown>;
}
\`\`\`

The \`ReactMarkdown\` component accepts markdown as children and renders it as React elements.

For syntax highlighting, also install \`react-syntax-highlighter\`:

\`\`\`bash
npm install react-syntax-highlighter
\`\`\`

Both packages work together to provide **complete markdown rendering** with code syntax highlighting.`;

// ============================================
// Example 9: Lists and Formatting
// ============================================
export const EXAMPLE_9_LISTS = `## Project Structure

### Frontend Directory

- **public/**
  - index.html - Main HTML file
  - favicon.ico
- **src/**
  - **components/** - React components
    - App.js
    - Header.js
  - **pages/** - Page components
  - App.css
  - index.js

### Backend Directory

1. app/
2. config/
3. tests/
4. requirements.txt

### Key Differences Between Ordered and Unordered Lists

**Unordered List** (bullet points):
- Item without specific order
- Can be reorganized
- Good for options or features

**Ordered List** (numbered):
1. First step in sequence
2. Second step in sequence
3. Order matters here`;

// ============================================
// Example 10: Error/Success Messages
// ============================================
export const EXAMPLE_10_MESSAGES = `## API Response Examples

### ✅ Success Response

\`\`\`json
{
  "status": "success",
  "code": 200,
  "data": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "message": "User retrieved successfully"
}
\`\`\`

### ❌ Error Response

\`\`\`json
{
  "status": "error",
  "code": 404,
  "error": "NOT_FOUND",
  "message": "User not found"
}
\`\`\`

### Response Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Authentication required |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |`;

// ============================================
// HOW TO TEST THESE EXAMPLES
// ============================================

/**
 * Testing Instructions:
 * 
 * 1. Open your chatbot UI in browser
 * 2. For each example below, you can either:
 *    a) Modify your backend to return this markdown
 *    b) Or create a debug endpoint that returns these examples
 * 
 * 3. Send a message and verify:
 *    - Headings render correctly
 *    - Code blocks display with syntax highlighting
 *    - Code language labels appear
 *    - Inline code appears inline (not as block)
 *    - Lists are properly formatted
 *    - Bold/italic text is styled
 *    - Blockquotes have border styling
 *    - Horizontal scroll works for long code lines
 *    - Mobile responsive design works
 * 
 * Debug Endpoint Example (Python/FastAPI):
 * 
 *   @app.get("/api/test-markdown/{example_id}")
 *   def get_test_markdown(example_id: int):
 *       examples = {
 *           1: EXAMPLE_1_PYTHON,
 *           2: EXAMPLE_2_JAVASCRIPT,
 *           ...
 *       }
 *       return {"response": examples.get(example_id, "Invalid example")}
 */

export const ALL_EXAMPLES = {
  1: EXAMPLE_1_PYTHON,
  2: EXAMPLE_2_JAVASCRIPT,
  3: EXAMPLE_3_SQL,
  4: EXAMPLE_4_JSON,
  5: EXAMPLE_5_MIXED,
  6: EXAMPLE_6_COMPLEX,
  7: EXAMPLE_7_MULTICODE,
  8: EXAMPLE_8_INLINE_CODE,
  9: EXAMPLE_9_LISTS,
  10: EXAMPLE_10_MESSAGES,
};
