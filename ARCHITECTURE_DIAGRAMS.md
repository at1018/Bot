# Architecture Diagram - Intelligent Query Detection System

## Flow Diagram 1: Complete Request Processing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER SENDS QUESTION                             │
│                    (via API endpoint /api/chat)                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    routes.py → ChatbotLLM.get_answer()                  │
│                    Receives: question, context, history                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  provider.invoke(question, context...)                  │
│                         (GeminiProvider,                                │
│                          AnthropicProvider,                             │
│                          OpenAIProvider,                                │
│                          GroqProvider)                                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BaseLLMProvider.setup_chain()                        │
│                   (Dynamic Prompt Injection)                            │
│                                                                         │
│     RunnableLambda processes:                                           │
│     {                                                                   │
│       "question": "Write a Python function",                            │
│       "conversation_context": "...",                                    │
│       "additional_context": "...",                                      │
│       "extraction_level": "Minimal extraction - ...",                   │
│       "system_prompt": ???  ← COMPUTED HERE                             │
│     }                                                                   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
        ┌───────────▼──────────┐  ┌──────────▼────────────┐
        │ _is_code_request()   │  │ _get_system_prompt()  │
        │                      │  │                       │
        │ Keyword detection:   │  │ if is_code:           │
        │ - 'python'        ✓  │  │   → Code Prompt       │
        │ - 'function'      ✓  │  │ else:                 │
        │ - 'code'          ✓  │  │   → Text Prompt       │
        │ - ... (40+ keys)     │  │                       │
        │                      │  │                       │
        │ Returns: True/False  │  │ Returns: String       │
        └──────────┬───────────┘  └──────────┬────────────┘
                   │                         │
                   └────────────┬────────────┘
                                │
                   ┌────────────▼────────────┐
                   │                         │
         ┌─────────▼────────────┐  ┌────────▼──────────┐
         │ CODE_SYSTEM_PROMPT   │  │ TEXT_SYSTEM_PROMPT│
         │                      │  │                   │
         │ SHORT (15 lines)     │  │ SHORT (18 lines)  │
         │                      │  │                   │
         │ "You are expert      │  │ "You are helpful  │
         │ code generation      │  │ articulate        │
         │ assistant"           │  │ assistant"        │
         │                      │  │                   │
         │ STRICT RULES:        │  │ FORMATTING:       │
         │ ✅ Triple backticks  │  │ ✅ Markdown (##)  │
         │ ✅ Proper indent     │  │ ✅ Bullets        │
         │ ✅ Code → Explain    │  │ ✅ Bold terms     │
         │ ✅ No plain code     │  │ ✅ Clear org      │
         │                      │  │                   │
         │ {extraction_level}   │  │ {extraction_level}│
         │ {conversation_ctx}   │  │ {conversation_ctx}│
         └─────────┬────────────┘  └────────┬──────────┘
                   │                         │
                   └────────────┬────────────┘
                                │
                         ┌──────▼──────┐
                         │ ChatTemplate│
                         │ Template    │
                         │             │
                         │ ("system",  │
                         │  "{sys_pm}")│
                         │ ("human",   │
                         │  "{quest}") │
                         └──────┬──────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   LLM Model             │
                    │  (Receives correct      │
                    │   prompt + context)     │
                    │                         │
                    │  Generates response:    │
                    │  - If Code: Backticks   │
                    │  - If Text: Structured  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ _format_code_response() │
                    │                         │
                    │ 1. Has backticks?       │
                    │    → Return as-is       │
                    │ 2. Has unwrapped code?  │
                    │    → Auto-wrap + detect │
                    │       language          │
                    │ 3. Plain text?          │
                    │    → Return as-is       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Formatted Response    │
                    │  (Properly structured)  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Return to User         │
                    │  (MessageResponse)      │
                    └─────────────────────────┘
```

---

## Flow Diagram 2: Query Type Detection Logic

```
┌──────────────────────────┐
│  User Question           │
│  "Write a Python func"   │
└────────┬─────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│  _is_code_request(question)                            │
│                                                        │
│  code_keywords = [                                     │
│    'python', 'javascript', 'java', 'code',            │
│    'function', 'script', 'program', 'write',          │
│    'create', 'build', 'implement', 'develop',         │
│    'sql', 'query', 'class', 'method', ...  (40+)      │
│  ]                                                     │
│                                                        │
│  question_lower = "write a python func"               │
│                                                        │
│  for keyword in code_keywords:                        │
│    if keyword in question_lower:  ← YES!              │
│      return True                                       │
└────────────────┬──────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │  is_code=True  │
        └────────┬───────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ CODE_SYSTEM_PROMPT  │
        │                     │
        │ "You are expert     │
        │  code generation    │
        │  assistant"         │
        │                     │
        │ - ALWAYS triple ``` │
        │ - Proper indent     │
        │ - Code structure    │
        │ - No plain code     │
        │                     │
        │ Format:             │
        │ Code → Explain      │
        │      → How to Run   │
        └─────────────────────┘
```

---

## Flow Diagram 3: Code Wrapping Logic

```
┌──────────────────────────────────────┐
│ LLM Response                          │
│ (Any format)                          │
└────────────┬─────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ _format_code_resp()│
    └────────┬───────────┘
             │
    ┌────────▼────────┐
    │ Has ``` ?       │
    └────────┬────────┘
             │
     ┌───────┴────────┐
     │                │
    YES              NO
     │                │
     ▼                ▼
  Return         ┌────────────────────┐
   as-is         │ Parse into lines   │
                 │                    │
                 │ for each line:     │
                 │   starts w/ spaces?│
                 │   or has keyword?  │
                 │   (def, import)    │
                 │                    │
                 │ → FOUND CODE BLOCK │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ _detect_language() │
                 │                    │
                 │ Check patterns:    │
                 │ - "def " → Python  │
                 │ - "function" → JS  │
                 │ - "public" → Java  │
                 │ - "select" → SQL   │
                 │ - else → plaintext │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Wrap Code Block    │
                 │                    │
                 │ ```python          │
                 │ <code lines>       │
                 │ ```                │
                 └─────────┬──────────┘
                           │
                           ▼
                 Return formatted
```

---

## Prompt Selection Matrix

```
┌─────────────────────────────────────────────────────────────┐
│              INTELLIGENT PROMPT SELECTION                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ QUERY CONTAINS:                    → APPLIES PROMPT:        │
│ ────────────────────────────────────────────────────────    │
│                                                             │
│ "python" / "code" / "function"     → CODE_SYSTEM_PROMPT     │
│ "write a script"                                           │
│ "create an API"                                            │
│ "implement algorithm"                                      │
│ "build a server"                                           │
│ "generate regex"                                           │
│ "fix this bug"                                             │
│                                                             │
│ ─────────────────────────────────────────────────────────   │
│                                                             │
│ "What is Python?"                  → TEXT_SYSTEM_PROMPT     │
│ "Explain machine learning"                                 │
│ "How does REST work?"                                      │
│ "Compare databases"                                        │
│ "Tell me about..."                                         │
│ Regular questions                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Provider Inheritance Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    BaseLLMProvider                             │
│                   (Abstract Class)                             │
│                                                                │
│   NEW INTELLIGENT METHODS:                                     │
│   ✅ _is_code_request(question) → bool                         │
│   ✅ _get_system_prompt(is_code) → str                         │
│   ✅ _get_code_system_prompt() → str                           │
│   ✅ _get_text_system_prompt() → str                           │
│   ✅ _detect_language(lines) → str                             │
│                                                                │
│   REFACTORED:                                                  │
│   ✅ setup_chain() - Dynamic prompt injection                  │
│   ✅ _format_code_response() - Intelligent wrapping            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                          ▲
                          │
                ┌─────────┼─────────┬──────────────┐
                │         │         │              │
                ▼         ▼         ▼              ▼
         ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
         │ Gemini   │ │Anthropic │ │ OpenAI   │ │  Groq    │
         │Provider  │ │Provider  │ │ Provider │ │ Provider │
         │          │ │          │ │          │ │          │
         │ ✅ No    │ │ ✅ No    │ │ ✅ No    │ │ ✅ No    │
         │   changes│ │   changes│ │   changes│ │   changes│
         │          │ │          │ │          │ │          │
         │ All methods               All methods inherit      │
         │ inherited from Base!                              │
         └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Code vs Text System Prompt Comparison

```
┌────────────────────────────────────────────────────────────────┐
│                    CODE_SYSTEM_PROMPT                          │
├────────────────────────────────────────────────────────────────┤
│ You are an expert code generation assistant.                  │
│                                                                │
│ ## CODE RESPONSE REQUIREMENTS                                 │
│                                                                │
│ **STRICT RULES - ALWAYS FOLLOW:**                             │
│                                                                │
│ 1. **ALWAYS wrap code in triple backticks with language**     │
│ 2. **INDENTATION MUST BE CORRECT**                            │
│ 3. **CODE STRUCTURE** (clear names, comments, error hdl.)    │
│ 4. **RESPONSE FORMAT** (Code → Explanation → How to Run)      │
│ 5. **NEVER RETURN PLAIN CODE** without backticks              │
│                                                                │
│ (15 lines total)                                              │
└────────────────────────────────────────────────────────────────┘
                              vs
┌────────────────────────────────────────────────────────────────┐
│                    TEXT_SYSTEM_PROMPT                          │
├────────────────────────────────────────────────────────────────┤
│ You are a helpful, articulate assistant that provides clear,  │
│ well-structured responses.                                    │
│                                                                │
│ ## RESPONSE REQUIREMENTS                                      │
│                                                                │
│ **FORMATTING RULES:**                                         │
│                                                                │
│ 1. **Use Markdown Structure** (##, ###, bullets, **bold**)   │
│ 2. **CLARITY AND ORGANIZATION** (direct → details → examples)│
│ 3. **AVOID** (code blocks, long paragraphs, verbosity)        │
│                                                                │
│ (18 lines total)                                              │
└────────────────────────────────────────────────────────────────┘
```

---

## Method Call Sequence

```
Diagram 1: Code Request Flow
═════════════════════════════

User: "Write Python code for factorial"
         │
         ▼
   provider.invoke(question="Write Python code for factorial", ...)
         │
         ▼
   setup_chain() called (during provider init)
         │
         ├─ Creates prompt_template with {system_prompt}
         │
         └─ Creates chain with RunnableLambda for system_prompt
                │
                └─ When chain executes:
                   ├─ RunnableLambda receives {question: "..."}
                   ├─ Calls _is_code_request("Write Python...")
                   │  ├─ Finds keyword "python" ✓
                   │  └─ Returns True
                   │
                   ├─ Calls _get_system_prompt(is_code=True)
                   │  ├─ Calls _get_code_system_prompt()
                   │  └─ Returns strict code prompt
                   │
                   └─ Injects into template
                      │
                      ▼
                   LLM Receives:
                   - system: "You are expert code generation..."
                   - human: "Write Python code for factorial"
                      │
                      ▼
                   LLM Generates:
                   ```python
                   def factorial(n):
                       ...
                   ```
                   ## Explanation
                   ...
                      │
                      ▼
                   _format_code_response() processes
                   - Sees ``` → returns as-is
                      │
                      ▼
                   User gets: properly formatted code

Diagram 2: Text Request Flow
════════════════════════════

User: "What is REST API?"
         │
         ▼
   provider.invoke(question="What is REST API?", ...)
         │
         ▼
   setup_chain() called
         │
         └─ When chain executes:
            ├─ RunnableLambda receives {question: "What is REST..."}
            ├─ Calls _is_code_request("What is REST...")
            │  ├─ No matching keywords
            │  └─ Returns False
            │
            ├─ Calls _get_system_prompt(is_code=False)
            │  ├─ Calls _get_text_system_prompt()
            │  └─ Returns structured text prompt
            │
            └─ Injects into template
               │
               ▼
            LLM Receives:
            - system: "You are helpful, articulate..."
            - human: "What is REST API?"
               │
               ▼
            LLM Generates:
            ## What is REST API?
            REST stands for...
            
            ## Key Principles
            - Stateless
            - Client-Server
            ...
               │
               ▼
            _format_code_response() processes
            - No ``` → returns as-is
               │
               ▼
            User gets: structured text response
```

---

## Benefits Summary Table

```
┌──────────────────────────────────────────────────────────────────┐
│                       ARCHITECTURE BENEFITS                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ BEFORE                                │ AFTER                   │
│ ──────────────────────────────────────┼─────────────────────── │
│                                       │                        │
│ ❌ Single 70-line prompt              │ ✅ Dynamic 15-18 line  │
│   (conflicting rules)                 │    (context-specific)  │
│                                       │                        │
│ ❌ Manual query analysis needed       │ ✅ 40+ keyword detect  │
│                                       │                        │
│ ❌ Inconsistent formatting            │ ✅ Guaranteed format   │
│                                       │    (code blocks work)   │
│                                       │                        │
│ ❌ Plain code responses               │ ✅ Auto-wrapped code   │
│                                       │                        │
│ ❌ Unstructured text                  │ ✅ Markdown formatted  │
│                                       │                        │
│ ❌ No language detection              │ ✅ Auto-detect language│
│                                       │                        │
│ ❌ Breaking code blocks               │ ✅ Preserved backticks │
│                                       │                        │
│ ❌ Manual intervention needed         │ ✅ Fully automated     │
│                                       │                        │
│ ❌ Different behavior per provider    │ ✅ Consistent all      │
│                                       │    providers           │
│                                       │                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: When Which Prompt Is Used

```
QUERY CONTAINS ANY OF:              → CODE PROMPT
═════════════════════════════════════════════════════════
python, javascript, java            Code languages
code, script, function              Generic code
write, create, build, implement     Action verbs
develop, develop, refactor          Dev operations
sql, query, database                Database terms
api, endpoint, server, client       Infrastructure
example, snippet, template          Code artifacts
demo, scaffold, generate            Generation
regex, algorithm, class, method     Code structures
react, angular, vue, node           Frameworks
express, django, flask              Web frameworks
debug, fix bug, error handling      Debugging


ALL OTHER QUERIES                  → TEXT PROMPT
═══════════════════════════════════════════════════════════
"What is Python?"                   Documentation
"Explain machine learning"          Explanations
"How does..."                       How-tos
"Tell me about..."                  Narratives
"Compare X and Y"                   Comparisons
"List the steps..."                 Instructions
etc.                                Any generic q&a
```

---

This comprehensive visual documentation shows exactly how the intelligent system works!
