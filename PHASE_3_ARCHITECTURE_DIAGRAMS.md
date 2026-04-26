# Phase 3 Architecture Diagrams

## 1. Main Enforcement Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Response Received                         │
│          (Raw text from Gemini/Anthropic/OpenAI/Groq)           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              _format_code_response() [Entry Point]               │
│              (Called by invoke() method)                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
        ╔═════════════════════════════════════════════════╗
        ║  _enforce_response_structure(text, is_code)    ║
        ║         [CRITICAL ENFORCEMENT GATE]            ║
        ║                                                 ║
        ║  Decision Point: Code or Text?                 ║
        ╚═════════════════════════════════════════════════╝
                  │                      │
         is_code=True             is_code=False
                  │                      │
                  ▼                      ▼
    ┌─────────────────────┐    ┌─────────────────────┐
    │ Validate Structure  │    │ Validate Structure  │
    │ (Code Checks)       │    │ (Text Checks)       │
    └────────┬────────────┘    └────────┬────────────┘
             │                         │
       Valid? ✓/✗                 Valid? ✓/✗
             │                         │
        ┌────┴─────┐              ┌────┴─────┐
        │           │              │           │
        ▼           ▼              ▼           ▼
      YES          NO            YES          NO
        │           │              │           │
        │    ┌──────────────────┐  │    ┌──────────────────┐
        │    │ Repair Code      │  │    │ Repair Text      │
        │    │ (3-tier fallback)│  │    │ (Add structure)  │
        │    └────────┬─────────┘  │    └────────┬─────────┘
        │             │            │             │
        └──────┬──────┘            └──────┬──────┘
               │                          │
               ▼                          ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │ _ensure_code_format │    │_ensure_text_format  │
        │                     │    │                     │
        │ Final Cleanup:      │    │ Final Cleanup:      │
        │ - Add Language ID   │    │ - Ensure Readable   │
        │ - Check Backticks   │    │ - Preserve Content  │
        │ - Build Structure   │    └────────┬────────────┘
        └────────┬────────────┘             │
                 │                         │
                 └──────────┬──────────────┘
                            │
                            ▼
                ┌─────────────────────────────────┐
                │  Guaranteed Properly Formatted  │
                │  Response Returned to User      │
                └─────────────────────────────────┘
```

## 2. Code Response Processing (Detailed)

```
┌──────────────────────────────────────────────────┐
│  Code Response: _enforce_response_structure()    │
│                                                  │
│  Input: Raw LLM text                             │
│  Intent: Ensure backticks + code structure       │
└──────────────────────────────────────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ _validate_Code_Response│
              │                        │
              │ Checks:                │
              │ - Has ```?             │
              │ - Code block valid?    │
              │ - Code non-empty?      │
              └────────┬───────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
         VALID                 INVALID
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ _repair_code_response│
            │          │                      │
            │          │ Strategy 1:          │
            │          │ Extract indented     │
            │          │ code + wrap          │
            │          │                      │
            │          │ Strategy 2:          │
            │          │ If looks like code,  │
            │          │ wrap all             │
            │          │                      │
            │          │ Strategy 3:          │
            │          │ Wrap as plaintext    │
            │          └──────┬───────────────┘
            │                 │
            └─────────┬───────┘
                      │
                      ▼
            ┌──────────────────────┐
            │_parse_code_response()│
            │                      │
            │ Extract:             │
            │ - Code block text    │
            │ - Language ID        │
            │ - Explanation sect.  │
            │ - Usage/How-to sect. │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ _ensure_code_format()│
            │                      │
            │ Rebuild Response:    │
            │ ```python            │
            │ <code>               │
            │ ```                  │
            │                      │
            │ ## Explanation       │
            │ <text>               │
            │                      │
            │ ## How to Run        │
            │ <instructions>       │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Guaranteed Formatted │
            │ Code Response        │
            │ ✓ Backticks present  │
            │ ✓ Language ID set    │
            │ ✓ Structure clear    │
            │ ✓ Indentation OK     │
            └──────────────────────┘
```

## 3. Code Repair Pipeline (3-Tier Fallback)

```
Code Repair: _repair_code_response(text)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    TIER 1            TIER 2            TIER 3
        │                  │                  │
        ▼                  ▼                  ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Extract Code   │ │ _looks_like_   │ │ Fallback:      │
│ Indicators     │ │ code() check    │ │ Wrap as        │
│                │ │                │ │ plaintext      │
│ - Find indent. │ │ If ≥2 code     │ │                │
│ - Find defs    │ │ indicators:    │ │ Returns:       │
│ - Find imports │ │ wrap entire    │ │ ```plaintext   │
│                │ │ text in ```    │ │ <text>         │
│ Extract:       │ │                │ │ ```            │
│ - Contiguous   │ │ Example:       │ │                │
│   lines        │ │ "def foo():"   │ │ Always safe    │
│ - Wrap in ```  │ │ "    pass"     │ │ fallback       │
│                │ │ Indicators: 2  │ │                │
│ Detect:        │ │ ✓ def + indent │ │                │
│ - Language     │ │                │ │                │
│                │ │                │ │                │
│ Success if:    │ │ Success if:    │ │ Success if:    │
│ Code found &   │ │ Looks like     │ │ Always         │
│ Wrapped        │ │ code           │ │ succeeds       │
└────────────────┘ └────────────────┘ └────────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Return Wrapped Code │
                │ (GUARANTEED)        │
                └─────────────────────┘
```

## 4. Text Response Processing (Simplified)

```
Text Response: _enforce_response_structure()
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    VALIDATE           PARSE               REPAIR
        │                  │                  │
        ▼                  ▼                  ▼
Has Content?     Extract:            Add Structure:
Has Structure?   - Headers          - Insert header
                 - Sections         - Preserve content
    │            - Lists            - Return enhanced
    ▼                 │                  │
 Valid?               ▼                  ▼
  │         ┌──────────────────┐   ┌─────────────────┐
  ▼         │ _parse_text_     │   │ _repair_text_   │
ENSURE      │ response()       │   │ response()      │
FORMAT      └──────┬───────────┘   └────────┬────────┘
  │                │                        │
  └────────┬───────┴────────────────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ Readable Response    │
  │ ✓ Has content       │
  │ ✓ Structured if long│
  │ ✓ Easy to read      │
  └──────────────────────┘
```

## 5. Language Detection Flow

```
Code Detection: _detect_language(code_lines)
                           │
                           ▼
        ┌──────────────────────────────┐
        │ Check Pattern Indicators     │
        └──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    PYTHON          JAVASCRIPT            JAVA
        │                  │                  │
    Check for:         Check for:         Check for:
    - def              - function         - public
    - import           - const            - private
    - class            - let              - class
    - print()          - var              - new
    - for/while        - console.log()    - import
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
       SQL            PLAINTEXT          (Continue)
         │                 │                 │
     Check for:        Default if:      Other langs
     - SELECT          No patterns       available
     - INSERT          match
     - UPDATE
         │
         └─────────────────┬─────────────────┘
                           │
                           ▼
              ┌──────────────────────┐
              │ Return Language ID   │
              │ (e.g., "python")     │
              └──────────────────────┘
```

## 6. Validation Gate Logic

```
_validate_response_structure(text, is_code)
                           │
                    ┌──────┴──────┐
                    │             │
               is_code?           │
                    │             │
            ┌───────┴────────┐    │
            │                │    │
         TRUE              FALSE  │
            │                │    │
            ▼                ▼    │
        CODE RULES      TEXT RULES│
            │                │    │
    Must have:         Must have: │
    - ```              - Content  │
    - Code content     - Min 10ch │
    - Non-empty        - If >100ch│
    - Valid format       structure│
            │                │    │
            └────────┬───────┘    │
                     │            │
                     ▼            │
            ┌──────────────────┐  │
            │ ALL CHECKS PASS? │  │
            └────────┬─────────┘  │
                     │            │
            ┌────────┴────────┐   │
            │                 │   │
            ▼                 ▼   │
          YES               NO    │
            │                │    │
            └────────┬───────┘    │
                     │            │
                     ▼            │
            ┌──────────────────┐  │
            │ (is_valid,       │  │
            │  error_message)  │  │
            └──────────────────┘  │
                                  │
```

## 7. Multi-Provider Auto-Inheritance

```
Phase 3 Methods Defined in BaseLLMProvider
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    GeminiProvider   AnthropicProvider   OpenAIProvider
    (Auto-inherit)   (Auto-inherit)      (Auto-inherit)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                    GroqProvider
                    (Auto-inherit)
                           │
                           ▼
        All 4 Providers Get Phase 3 Benefits
        - Identical code enforcement
        - Same quality guarantees
        - Zero code duplication
        - One maintenance point
```

## 8. Response Quality Gate

```
Input: LLM Response
         │
         ▼
┌──────────────────┐
│ Intent Detection │  (Existing: Phase 1-2)
│ Is Code? Yes/No  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Dynamic Prompt   │  (Existing: Phase 1-2)
│ Context Injected │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM Invoked      │  (Existing: Phase 1-2)
│ Response Made    │
└────────┬─────────┘
         │
         ▼  ⚠️  LLM May Not Follow Instructions
         │      (Prompt-only unreliable)
         │
         ▼
┌──────────────────────────────────┐
│ CRITICAL: Phase 3 Enforcement    │  (NEW)
│ Parse → Validate → Repair → Ensure
│                                  │
│ Deterministic Output Guaranteed  │
└────────┬───────────────────────┬─┘
         │                       │
    Quality ✓                 Quality ✓
    Response                  Response
    (Backticks,               (Structure,
     Language,                Content,
     Format)                  Readable)
```

## Summary

The Phase 3 pipeline transforms output from **prompt-dependent** (unreliable) to **deterministically enforced** (guaranteed). Each response passes through multiple validation and repair gates, ensuring consistent, properly-formatted output regardless of LLM behavior.
