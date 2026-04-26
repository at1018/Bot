"""Base class for LLM providers."""
from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from typing import Optional
import re


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        extraction_level: int = 1,
    ):
        """
        Initialize the LLM provider.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature for model sampling (0-1)
            max_tokens: Maximum tokens in response
            extraction_level: Level of data extraction (1=minimal, 2=medium, 3=detailed)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extraction_level = extraction_level
        self.llm = None
        self.chain = None
        
    @abstractmethod
    def initialize(self):
        """Initialize the LLM client with provider-specific configuration."""
        pass
    
    def _is_code_request(self, question: str) -> bool:
        """
        Detect if the user's question is asking for code.
        
        Uses keyword-based detection for common code request patterns.
        
        Args:
            question: The user's question
            
        Returns:
            True if the question appears to be requesting code, False otherwise
        """
        code_keywords = [
            'python', 'javascript', 'java', 'code', 'function', 'script',
            'program', 'write', 'create', 'build', 'implement', 'develop',
            'sql', 'query', 'class', 'method', 'algorithm', 'application',
            'api', 'endpoint', 'library', 'module', 'package', 'framework',
            'example', 'demo', 'snippet', 'template', 'scaffold', 'generate',
            'refactor', 'optimize', 'fix bug', 'debug', 'error handling',
            'regex', 'database', 'server', 'client', 'middleware',
            'html', 'css', 'react', 'angular', 'vue', 'node', 'express',
            'django', 'flask', 'fastapi', 'spring', 'kotlin', 'go', 'rust'
        ]
        
        question_lower = question.lower()
        
        # Check if any code keyword is in the question
        return any(keyword in question_lower for keyword in code_keywords)
    
    def _get_system_prompt(self, is_code: bool) -> str:
        """
        Generate a dynamic system prompt based on query type.
        
        Args:
            is_code: If True, return strict code formatting prompt. Otherwise, structured text prompt.
            
        Returns:
            The system prompt string
        """
        if is_code:
            return self._get_code_system_prompt()
        else:
            return self._get_text_system_prompt()
    
    def _get_code_system_prompt(self) -> str:
        """
        Get system prompt for code requests.
        
        Enforces strict code formatting rules.
        
        Returns:
            System prompt for code generation
        """
        return """You are an expert code generation assistant.

## CODE RESPONSE REQUIREMENTS

**STRICT RULES - ALWAYS FOLLOW:**

1. **ALWAYS wrap code in triple backticks with language identifier**
   Example: ```python, ```javascript, ```java, ```sql

2. **INDENTATION MUST BE CORRECT**
   - Python: 4 spaces per level
   - JavaScript/Java: 2-4 spaces per level
   - Preserve all formatting

3. **CODE STRUCTURE**
   - Clear variable names
   - Comments for complex logic
   - Error handling where applicable
   - Logical organization

4. **RESPONSE FORMAT**
   - First: Complete code in triple backticks
   - Then: ## Explanation section
   - Then: ## How to Run section (if applicable)
   - Include examples if helpful

5. **NEVER RETURN PLAIN CODE** without backticks

## EXTRACTION LEVEL: {extraction_level}

{conversation_context}

{additional_context}"""
    
    def _get_text_system_prompt(self) -> str:
        """
        Get system prompt for non-code requests.
        
        Returns:
            System prompt for structured text responses
        """
        return """You are a helpful, articulate assistant that provides clear, well-structured responses.

## RESPONSE REQUIREMENTS

**FORMATTING RULES:**

1. **Use Markdown Structure**
   - Use headers (##, ###) to organize information
   - Use bullet points for lists
   - Use **bold** for important terms
   - Use numbered lists for steps

2. **CLARITY AND ORGANIZATION**
   - Start with direct answer
   - Support with details
   - Use examples when helpful
   - Keep text readable and concise

3. **AVOID**
   - Unnecessary code blocks in text responses
   - Long paragraphs without structure
   - Overly verbose explanations
   - Redundant repetition

## EXTRACTION LEVEL: {extraction_level}

{conversation_context}

{additional_context}"""
    
    def setup_chain(self):
        """
        Setup the LangChain chain with dynamic system prompts.
        
        Uses RunnableLambda to determine system prompt at runtime based on query type.
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{question}")
        ])
        
        # Chain with dynamic system prompt injection
        self.chain = (
            {
                "question": RunnablePassthrough(),
                "conversation_context": RunnablePassthrough(),
                "additional_context": RunnablePassthrough(),
                "extraction_level": RunnableLambda(lambda _: self._format_extraction_level()),
                # Key: Dynamically determine system prompt based on question
                "system_prompt": RunnableLambda(lambda x: self._get_system_prompt(
                    self._is_code_request(x.get("question", ""))
                )),
            }
            | prompt_template
            | self.llm
        )
    
    def _format_extraction_level(self) -> str:
        """Format extraction level for the prompt."""
        levels = {
            1: "Minimal extraction - provide concise, direct answers",
            2: "Medium extraction - include relevant context and examples",
            3: "Detailed extraction - provide comprehensive information with deep analysis"
        }
        return levels.get(self.extraction_level, levels[1])
    
    @abstractmethod
    def invoke(self, question: str, conversation_context: str = "", additional_context: str = "") -> str:
        """
        Invoke the LLM with the given question.
        
        Args:
            question: The user's question
            conversation_context: Previous conversation history
            additional_context: Additional context for the question
            
        Returns:
            The LLM's response
        """
        pass
    
    def set_extraction_level(self, level: int):
        """Set the extraction level for data extraction."""
        if 1 <= level <= 3:
            self.extraction_level = level
        else:
            raise ValueError("Extraction level must be between 1 and 3")
    
    def get_extraction_level(self) -> int:
        """Get the current extraction level."""
        return self.extraction_level
    
    def _format_code_response(self, text: str) -> str:
        """
        CRITICAL: Post-process response to ensure proper code block formatting with enforcement.
        
        This is the primary enforcement gate for code responses. It implements a 2-PASS SYSTEM:
        1. PASS 1 → Python parsing, validation, repair (Phase 3 logic)
        2. PASS 2 → LLM reformatting for final polish (2-pass system)
        
        Args:
            text: The raw response from the model
            
        Returns:
            Properly formatted code response with guaranteed structure
        """
        # PASS 1: Apply the critical Python enforcement layer (Phase 3)
        enforced_text = self._enforce_response_structure(text, is_code=True)
        enforced_text = self._ensure_code_format(enforced_text)
        
        # PASS 2: Use LLM to reformat for final polish (2-pass system)
        final_text = self._reformat_response(enforced_text, is_code=True)
        
        return final_text
    
    def _detect_language(self, lines: list) -> str:
        """
        Detect programming language from code lines.
        
        Args:
            lines: List of code lines
            
        Returns:
            Language identifier (e.g., 'python', 'javascript', 'java')
        """
        code_text = '\n'.join(lines).lower()
        
        # Check for language indicators
        if any(keyword in code_text for keyword in ['def ', 'import ', 'class ', 'print(', 'for ', 'while ']):
            return 'python'
        elif any(keyword in code_text for keyword in ['function ', 'const ', 'let ', 'var ', 'console.log']):
            return 'javascript'
        elif any(keyword in code_text for keyword in ['public ', 'private ', 'class ', 'new ', 'import ']):
            return 'java'
        elif any(keyword in code_text for keyword in ['select ', 'from ', 'where ', 'insert ', 'update ']):
            return 'sql'
        else:
            return 'plaintext'
    
    # ============================================================================
    # CRITICAL: DETERMINISTIC OUTPUT PARSING & ENFORCEMENT LAYER
    # ============================================================================
    
    def _parse_code_response(self, text: str) -> dict:
        """
        Parse a code response into structured components.
        
        Extracts: code blocks, language, explanation, and usage instructions.
        
        Args:
            text: The raw response from the model
            
        Returns:
            dict with keys: 'code', 'language', 'explanation', 'usage', 'raw', 'is_valid'
        """
        result = {
            'code': '',
            'language': 'plaintext',
            'explanation': '',
            'usage': '',
            'raw': text,
            'is_valid': False
        }
        
        # Extract code blocks using regex
        code_block_pattern = r'```(\w*)\n(.*?)\n```'
        code_matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if code_matches:
            # Get first code block
            language, code = code_matches[0]
            result['language'] = language if language else 'plaintext'
            result['code'] = code.strip()
            result['is_valid'] = bool(result['code'])
            
            # Extract explanation and usage sections
            explanation_match = re.search(r'##\s*Explanation\s*\n(.*?)(?=##|$)', text, re.DOTALL)
            if explanation_match:
                result['explanation'] = explanation_match.group(1).strip()
            
            usage_match = re.search(r'##\s*(?:How to Run|Usage|Example)\s*\n(.*?)(?=##|$)', text, re.DOTALL)
            if usage_match:
                result['usage'] = usage_match.group(1).strip()
        
        return result
    
    def _parse_text_response(self, text: str) -> dict:
        """
        Parse a text response into structured components.
        
        Extracts: main content, sections, lists, and structure validation.
        
        Args:
            text: The raw response from the model
            
        Returns:
            dict with keys: 'content', 'sections', 'has_structure', 'raw'
        """
        result = {
            'content': text,
            'sections': [],
            'has_structure': False,
            'raw': text
        }
        
        lines = text.split('\n')
        
        # Check for headers
        header_pattern = r'^#{1,3}\s+'
        has_headers = any(re.match(header_pattern, line) for line in lines)
        
        # Check for lists
        has_lists = any(line.strip().startswith(('- ', '* ', '1. ', '2. ')) for line in lines)
        
        # Extract sections
        current_section = None
        for line in lines:
            header_match = re.match(header_pattern, line)
            if header_match:
                section_name = line.replace('#', '').strip()
                current_section = {
                    'name': section_name,
                    'content': ''
                }
                result['sections'].append(current_section)
            elif current_section is not None:
                current_section['content'] += line + '\n'
        
        result['has_structure'] = has_headers or has_lists
        
        return result
    
    def _validate_response_structure(self, text: str, is_code: bool) -> tuple[bool, str]:
        """
        Validate that response matches expected structure.
        
        CRITICAL VALIDATION: Ensures output matches intent.
        
        Args:
            text: The response text
            is_code: Whether this should be a code response
            
        Returns:
            tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Response is empty"
        
        if is_code:
            # Code response MUST have triple backticks
            if '```' not in text:
                return False, "Code response missing triple backticks"
            
            # Extract code
            code_match = re.search(r'```(\w*)\n(.*?)\n```', text, re.DOTALL)
            if not code_match:
                return False, "Invalid code block format"
            
            language, code = code_match.groups()
            
            # Validate code is not empty
            if not code.strip():
                return False, "Code block is empty"
            
            # Code should be reasonably sized (not just one line)
            code_lines = code.strip().split('\n')
            if len(code_lines) < 1:
                return False, "Code too short"
            
            return True, ""
        else:
            # Text response should have some structure or content
            if len(text.strip()) < 10:
                return False, "Response too short"
            
            # Should have either headers, lists, or be reasonably formatted
            has_headers = '##' in text or '###' in text
            has_lists = re.search(r'^\s*[-*]\s', text, re.MULTILINE)
            has_numbered = re.search(r'^\s*\d+\.\s', text, re.MULTILINE)
            
            # At least some structure is preferred but not mandatory for short responses
            if len(text) > 100:
                if not (has_headers or has_lists or has_numbered):
                    return False, "Long response lacks structure"
            
            return True, ""
    
    def _enforce_response_structure(self, text: str, is_code: bool) -> str:
        """
        CRITICAL: Enforce deterministic response structure.
        
        This is the final gatekeeper to ensure output matches expected structure.
        If validation fails, attempts to repair the response.
        
        Args:
            text: The raw response from the model
            is_code: Whether this should be a code response
            
        Returns:
            Properly formatted response guaranteed to match structure
        """
        is_valid, error_msg = self._validate_response_structure(text, is_code)
        
        if is_valid:
            # Validation passed - ensure formatting is correct
            if is_code:
                return self._ensure_code_format(text)
            else:
                return self._ensure_text_format(text)
        else:
            # Validation failed - attempt repair
            if is_code:
                return self._repair_code_response(text)
            else:
                return self._repair_text_response(text)
    
    def _repair_code_response(self, text: str) -> str:
        """
        Repair a code response that fails validation.
        
        Attempts to extract and reformat code properly.
        
        Args:
            text: The malformed response
            
        Returns:
            Properly formatted code response with fallback structures
        """
        # Strategy 1: Look for code blocks even if format is wrong
        possible_code = re.search(
            r'(?:^|\n)((?:[ \t]{4,}|def |class |import |function |const |let |var ).*)$',
            text,
            re.MULTILINE | re.DOTALL
        )
        
        if possible_code:
            # Extract contiguous code lines
            code_lines = []
            in_code = False
            
            for line in text.split('\n'):
                is_code_line = (
                    line.startswith('    ') or line.startswith('\t') or 
                    any(kw in line for kw in ['def ', 'class ', 'import ', 'function ', 'const ', 'let ', 'var ', 'return ', 'if ', 'for '])
                )
                
                if is_code_line:
                    code_lines.append(line)
                    in_code = True
                elif in_code and line.strip() == '':
                    code_lines.append(line)
                elif in_code and not is_code_line:
                    break
            
            if code_lines:
                code = '\n'.join(code_lines).strip()
                if code:
                    language = self._detect_language(code_lines)
                    explanation = text.replace(code, '').strip()
                    
                    result = f"```{language}\n{code}\n```"
                    if explanation:
                        result += f"\n\n## Explanation\n{explanation}"
                    
                    return result
        
        # Strategy 2: If text looks like code, wrap it entirely
        if self._looks_like_code(text):
            language = self._detect_language(text.split('\n'))
            return f"```{language}\n{text}\n```"
        
        # Strategy 3: Fallback - wrap as plaintext
        return f"```plaintext\n{text}\n```"
    
    def _repair_text_response(self, text: str) -> str:
        """
        Repair a text response that fails validation.
        
        Attempts to add structure if missing or salvage content.
        
        Args:
            text: The unstructured response
            
        Returns:
            Minimally structured text response
        """
        text = text.strip()
        lines = text.split('\n')
        
        # If already has headers, return as-is
        if any(line.startswith('#') for line in lines):
            return text
        
        # If very short, just return as-is
        if len(text) < 50:
            return text
        
        # Add header to first line if it's a complete statement
        if lines and not lines[0].startswith('#'):
            first_line = lines[0].strip()
            # If first line looks like a heading (short, not a full sentence), make it one
            if first_line and len(first_line) < 80 and not first_line.endswith('.'):
                lines[0] = f"## {first_line}"
            else:
                # Otherwise insert a generic header
                lines.insert(0, "## Response")
        
        return '\n'.join(lines)
    
    def _ensure_code_format(self, text: str) -> str:
        """
        Ensure code response has proper format.
        
        - Language identifier present
        - Proper code block markers
        - Expected sections
        
        Args:
            text: Text with code
            
        Returns:
            Properly formatted code response
        """
        # Parse existing code
        parsed = self._parse_code_response(text)
        
        if parsed['code']:
            # Ensure language is set
            if not parsed['language'] or parsed['language'] == 'plaintext':
                code_lines = parsed['code'].split('\n')
                parsed['language'] = self._detect_language(code_lines)
            
            # Build formatted response
            result = f"```{parsed['language']}\n{parsed['code']}\n```"
            
            if parsed['explanation']:
                result += f"\n\n## Explanation\n{parsed['explanation']}"
            
            if parsed['usage']:
                result += f"\n\n## How to Run\n{parsed['usage']}"
            
            return result
        
        return text
    
    def _ensure_text_format(self, text: str) -> str:
        """
        Ensure text response has proper format.
        
        Args:
            text: Text to format
            
        Returns:
            Properly formatted text response
        """
        return text
    
    def _looks_like_code(self, text: str) -> bool:
        """
        Heuristic check if text looks like code.
        
        Args:
            text: The text to check
            
        Returns:
            True if text appears to be code
        """
        code_indicators = [
            'def ', 'class ', 'import ', 'function ', 'const ', 'let ', 'var ',
            'if ', 'for ', 'while ', 'return ', 'async ', 'await ',
            'try ', 'except ', 'finally ', '=>', '->', '()', '{}', '[]'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for ind in code_indicators if ind in text_lower)
        
        # More than 2 code indicators = likely code
        return indicator_count >= 2
    
    # ============================================================================
    # 2-PASS SYSTEM: LLM REFORMATTING (PASS 2)
    # ============================================================================
    
    def _reformat_response(self, text: str, is_code: bool) -> str:
        """
        PASS 2: Use LLM to reformat response for final polish and consistency.
        
        This is the second pass of the 2-pass system:
        - PASS 1: Main LLM generation (with intent-based prompt)
        - PASS 2: This method - LLM reformatting for strict structure
        
        Args:
            text: The response from PASS 1 (already Python-validated by Phase 3)
            is_code: Whether this is a code response
            
        Returns:
            The reformatted response from the LLM
        """
        if not text or not text.strip():
            return text
        
        # Get the reformatting prompt based on intent
        reformat_prompt = self._get_reformat_prompt(is_code)
        
        # Create a simple reformatting chain
        try:
            reformat_template = ChatPromptTemplate.from_messages([
                ("system", reformat_prompt),
                ("human", f"Reformat this response:\n\n{text}")
            ])
            
            reformat_chain = reformat_template | self.llm
            reformatted = reformat_chain.invoke({})
            
            # Extract text from response object
            if hasattr(reformatted, 'content'):
                return reformatted.content
            else:
                return str(reformatted)
        except Exception as e:
            # If reformatting fails, return original text
            print(f"Warning: Reformatting failed, using original response: {e}")
            return text
    
    def _get_reformat_prompt(self, is_code: bool) -> str:
        """
        Get the reformatting prompt for PASS 2.
        
        This prompt is STRICT and focused solely on formatting, not content generation.
        
        Args:
            is_code: If True, return code reformatting prompt. Otherwise, text reformatting prompt.
            
        Returns:
            The reformatting system prompt
        """
        if is_code:
            return """You are a code formatter. Your ONLY job is to ensure the code is perfectly formatted.

## CODE REFORMATTING RULES (STRICT - APPLY TO ALL CODE)

1. **BACKTICKS ARE MANDATORY**
   - Wrap ALL code in triple backticks: ```language
   - Always include language identifier: python, javascript, java, sql, etc.

2. **CODE STRUCTURE**
   - Correct indentation (Python: 4 spaces, others: 2-4 spaces)
   - No trailing whitespace
   - Preserve all logic and content

3. **RESPONSE FORMAT (STRICT ORDER)**
   - FIRST: Code block with triple backticks and language identifier
   - SECOND: ## Explanation (brief description of what code does)
   - THIRD: ## How to Run (usage instructions if applicable)

4. **NEVER MODIFY LOGIC**
   - Only fix formatting, indentation, backticks
   - Do NOT change the actual code

5. **OUTPUT MUST BE**
   - Clean and readable
   - Properly structured with sections
   - Ready for immediate use

Return ONLY the reformatted response. No preamble."""
        else:
            return """You are a text formatter. Your ONLY job is to ensure the text is perfectly formatted.

## TEXT REFORMATTING RULES (STRICT - APPLY TO ALL TEXT)

1. **STRUCTURE IS MANDATORY**
   - Use headers (## Main Topic, ### Sub-topics)
   - Use bullet points for lists
   - Use **bold** for important terms
   - Number steps when applicable

2. **CLARITY**
   - Clear and concise language
   - No unnecessary verbosity
   - Easy to scan and read

3. **CONTENT PRESERVATION**
   - Keep all original information
   - Do NOT add or remove content
   - Only improve formatting and structure

4. **FORMATTING RULES**
   - One main section at top
   - Sub-sections with ###
   - Bullet points for lists
   - **Bold** for key terms
   - Proper spacing between sections

5. **OUTPUT MUST BE**
   - Well-organized
   - Easy to read
   - Properly structured
   - Immediately usable

Return ONLY the reformatted response. No preamble."""
