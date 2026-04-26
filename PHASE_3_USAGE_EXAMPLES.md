# Phase 3: Practical Usage Examples

## Overview
Phase 3 automatically enforces proper output structure. Users don't need to do anything special - the enforcement happens transparently during response processing.

## How It Works Automatically

### Code Request Flow

**User asks for code:**
```
User: "Write a Python function to check if a number is prime"
```

**Provider detects it's a code request** (via `_is_code_request()`)
- Keyword matching finds: "Write", "function", "Python" → Code request ✓

**Dynamic system prompt injected** (via Phase 2)
- Code-specific prompt with strict formatting rules applied
- LLM guided toward proper backticks and structure

**LLM responds** (May or may not follow instructions)
- Best case: Returns proper code with backticks
- Worst case: Returns plain code without formatting

**Phase 3 enforcement applies** (Automatic)
1. `_enforce_response_structure()` validates response
2. If improper format detected, repairs via `_repair_code_response()`
3. `_ensure_code_format()` final cleanup
4. **Guaranteed output has backticks and proper structure**

**User receives properly formatted code**
```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

## Example 1: Proper Code Response (No Repair Needed)

### Scenario
```
Provider: GeminiProvider
Question: "Write Python code to reverse a string"
LLM_Response: "```python
def reverse_string(s):
    return s[::-1]

# Usage:
result = reverse_string('hello')
print(result)  # Output: olleh
```"
```

### What Happens
1. **Validation**: Response already has backticks → ✓ VALID
2. **Processing**: No repair needed
3. **Output**: Returned as-is with final format cleanup

### User Receives
```
```python
def reverse_string(s):
    return s[::-1]

# Usage:
result = reverse_string('hello')
print(result)  # Output: olleh
```
```

---

## Example 2: Broken Format - No Backticks

### Scenario
```
Provider: AnthropicProvider
Question: "Write JavaScript code to sort an array"
LLM_Response: "function sortArray(arr) {
    return arr.sort((a, b) => a - b);
}

Example usage:
const numbers = [3, 1, 4, 1, 5];
const sorted = sortArray(numbers);"
```
(Note: No triple backticks, just plain code)

### What Happens
1. **Detection**: LLM didn't follow backtick instruction
2. **Validation**: No ``` found → ✗ INVALID
3. **Repair Strategy 1**: 
   - Detects indented patterns and code keywords (function, const, return)
   - Extracts contiguous code block
   - Detects language (JavaScript from keywords)
4. **Wrapping**: Adds triple backticks with language identifier
5. **Final Format**: Applies `_ensure_code_format()`

### User Receives (Auto-Repaired)
```javascript
function sortArray(arr) {
    return arr.sort((a, b) => a - b);
}

Example usage:
const numbers = [3, 1, 4, 1, 5];
const sorted = sortArray(numbers);
```
(Now with proper backticks and JavaScript language identifier!)

---

## Example 3: Code Mixed with Text (No Structure)

### Scenario
```
Provider: OpenAIProvider
Question: "Show me Java code to read a file"
LLM_Response: "import java.io.File;
import java.util.Scanner;

public class FileReader {
    public static void main(String[] args) throws Exception {
        File file = new File('data.txt');
        Scanner scanner = new Scanner(file);
        while (scanner.hasNextLine()) {
            System.out.println(scanner.nextLine());
        }
    }
}

This code creates a FileReader class that uses Scanner to read lines from a file. It imports necessary classes and the main method opens the file and prints each line. Remember to handle exceptions properly!"
```

### What Happens
1. **Detection**: Code pattern detected (public class, import, main method)
2. **Validation**: No ``` found → ✗ INVALID
3. **Repair**: 
   - Strategy 1 extracts indented code lines
   - Identifies language (Java from keywords: public, class, import)
   - Separates code from explanation
4. **Reconstruction**: Builds proper structure with code block + explanation sections

### User Receives (Auto-Repaired with Structure)
```
```java
import java.io.File;
import java.util.Scanner;

public class FileReader {
    public static void main(String[] args) throws Exception {
        File file = new File('data.txt');
        Scanner scanner = new Scanner(file);
        while (scanner.hasNextLine()) {
            System.out.println(scanner.nextLine());
        }
    }
}
```

## Explanation
This code creates a FileReader class that uses Scanner to read lines from a file. It imports necessary classes and the main method opens the file and prints each line.

**Note:** Remember to handle exceptions properly!
```

---

## Example 4: Text Response (No Code)

### Scenario
```
Provider: GroqProvider
Question: "Explain what is recursion in programming"
LLM_Response: "Recursion is a technique where a function calls itself to solve smaller instances of the same problem. Key components are:
- Base case: stops the recursion
- Recursive case: breaks down the problem
- Call stack: manages nested calls

Example: factorial(5) → 5 * factorial(4) → ... → 1
Recursion is powerful but can be inefficient if not optimized."
```

### What Happens
1. **Detection**: No code keywords detected → Text response
2. **Validation**: Has content, length >100 chars, but lacks headers → ⚠️
3. **Repair**: Adds headers for structure
4. **Output**: Ensures readability

### User Receives (With Added Structure)
```
## Recursion in Programming
Recursion is a technique where a function calls itself to solve smaller instances of the same problem. Key components are:
- Base case: stops the recursion
- Recursive case: breaks down the problem
- Call stack: manages nested calls

Example: factorial(5) → 5 * factorial(4) → ... → 1
Recursion is powerful but can be inefficient if not optimized.
```

---

## Example 5: Edge Case - Very Short Response

### Scenario
```
Question: "What is a loop?"
LLM_Response: "A loop repeats code."
```

### What Happens
1. **Detection**: Text response, short content (<50 chars)
2. **Validation**: Very short → ✓ VALID (short responses exempt from structure requirement)
3. **Output**: Returned as-is

### User Receives
```
A loop repeats code.
```
(No headers added because too short)

---

## Example 6: Testing All Providers

### Gemini
```python
from app.models.gemini import GeminiProvider

provider = GeminiProvider(api_key="...", model_name="gemini-pro")

# Phase 3 enforcement applies automatically
response = provider.invoke("Write Python code to calculate GCD")
print(response)  # ✓ Guaranteed backticks + proper format
```

### Anthropic
```python
from app.models.anthropic import AnthropicProvider

provider = AnthropicProvider(api_key="...", model_name="claude-3-opus")

# Phase 3 enforcement applies automatically
response = provider.invoke("Show me JavaScript async/await example")
print(response)  # ✓ Guaranteed backticks + proper format
```

### OpenAI
```python
from app.models.openai import OpenAIProvider

provider = OpenAIProvider(api_key="...", model_name="gpt-4")

# Phase 3 enforcement applies automatically
response = provider.invoke("SQL query to find duplicate records")
print(response)  # ✓ Guaranteed backticks + proper format
```

### Groq
```python
from app.models.groq import GroqProvider

provider = GroqProvider(api_key="...", model_name="mixtral-8x7b")

# Phase 3 enforcement applies automatically
response = provider.invoke("Explain OOP principles")
print(response)  # ✓ Guaranteed structure + readability
```

All providers auto-inherit Phase 3 enforcement with **zero code changes needed**.

---

## What Gets Enforced

### For Code Responses
✅ **Always Has:**
- Triple backticks (```)
- Language identifier (python, javascript, java, sql, etc.)
- Non-empty code content
- Proper indentation preserved

✅ **Sections Preserved:**
- Code block
- Explanation (if provided by LLM)
- How to Run / Usage (if provided by LLM)

### For Text Responses
✅ **Always Has:**
- Non-empty content
- Minimal structure (headers if long response)
- Readability preserved

✅ **No Data Loss:**
- All original content kept
- Only formatting added

---

## Advanced: Monitoring Repair Operations

If you want to see what Phase 3 is doing behind the scenes:

```python
# Manually call parsing to inspect structure
provider = GeminiProvider(...)
response = provider.invoke("Write Python code...")

# Parse response to see what was extracted
parsed = provider._parse_code_response(response)
print(f"Language: {parsed['language']}")
print(f"Code lines: {len(parsed['code'].split(chr(10)))}")
print(f"Has explanation: {bool(parsed['explanation'])}")
print(f"Is valid: {parsed['is_valid']}")
```

---

## Quick Reference: What Changed Between Phases

| Feature | Phase 2 | Phase 3 |
|---------|---------|---------|
| Intent Detection | ✓ Working | ✓ Unchanged |
| Dynamic Prompts | ✓ Working | ✓ Unchanged |
| Format Preservation | ✓ Basic | ✓ Enhanced |
| Validation | ✗ None | ✓ **NEW** |
| Repair | ✗ None | ✓ **NEW** |
| Guarantee | Prompt-only | ✓ **Deterministic** |

---

## Summary

Phase 3 enforcement is **automatic and transparent**:
- Users don't need to do anything special
- All 4 providers get the same guarantees
- Responses are always properly formatted
- No data loss in repair process
- Zero configuration needed
