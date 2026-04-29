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
    
    def _detect_intent(self, question: str) -> str:
        """
        Detect the intent of the user's question using the LLM.
        
        Uses the LLM to intelligently classify the question intent rather than keyword matching.
        This enables accurate detection of nuanced queries like "what is python" (concept)
        vs "write a python function" (code).
        
        Args:
            question: The user's question
            
        Returns:
            Intent classification: 'code', 'explanation', 'analysis', 'how-to', 'other'
        """
        if not self.llm:
            # Fallback if LLM not initialized
            return 'other'
        
        intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier. Analyze the user's question and classify it into ONE of these categories:

- 'code': User explicitly wants code (write, implement, create, generate, fix, debug)
- 'explanation': User wants conceptual explanation or understanding
- 'analysis': User wants analysis, comparison, or breakdown
- 'how-to': User wants step-by-step instructions or guidance
- 'other': Doesn't fit above categories

Respond with ONLY the category name, nothing else. No explanation."""),
            ("human", f"Question: {question}")
        ])
        
        try:
            intent_chain = intent_prompt | self.llm
            response = intent_chain.invoke({})
            
            # Extract intent from response
            intent_text = response.content.strip().lower() if hasattr(response, 'content') else str(response).lower()
            
            # Validate and return valid intent
            valid_intents = ['code', 'explanation', 'analysis', 'how-to', 'other']
            for intent in valid_intents:
                if intent in intent_text:
                    return intent
            
            return 'other'
        except Exception as e:
            print(f"Warning: Intent detection failed, defaulting to 'other': {e}")
            return 'other'
    
    def _get_system_prompt(self, intent: str) -> str:
        """
        Generate a natural, ChatGPT-like system prompt based on detected intent.
        
        Instead of forcing rigid templates, provides flexible guidance that lets
        the LLM format responses naturally.
        
        Args:
            intent: The detected intent ('code', 'explanation', 'analysis', 'how-to', 'other')
            
        Returns:
            The system prompt string
        """
        if intent == 'code':
            return self._get_code_system_prompt()
        elif intent == 'explanation':
            return self._get_explanation_system_prompt()
        elif intent == 'analysis':
            return self._get_analysis_system_prompt()
        elif intent == 'how-to':
            return self._get_howto_system_prompt()
        else:
            return self._get_default_system_prompt()
    
    def _get_code_system_prompt(self) -> str:
        """
        System prompt for code requests - natural and flexible.
        
        Returns:
            System prompt for code generation
        """
        return """You are a helpful coding assistant that writes clear, working code.

When responding to code requests:
- Provide code in ```language code blocks (e.g. ```python, ```javascript)
- Use proper indentation and formatting
- Include comments for complex logic
- Add a brief explanation ONLY if it helps understand the code
- Include usage examples ONLY if they're necessary
- Format naturally, don't force rigid structure

Write code that is:
- Correct and working
- Well-organized
- Easy to understand
- Production-ready where applicable

Extraction level: {extraction_level}

{conversation_context}

{additional_context}"""

    def _get_explanation_system_prompt(self) -> str:
        """
        System prompt for concept/explanation requests - natural and conversational.
        
        Returns:
            System prompt for explanations
        """
        return """You are a helpful tutor that explains concepts clearly.

When responding to explanation requests:
- Provide clear, natural explanations
- Use examples to illustrate concepts
- Organize with headers only when helpful (not forced)
- Use bullet points only when needed for clarity
- Avoid unnecessary jargon
- Format like a natural conversation, not a rigid template

Write explanations that are:
- Easy to understand
- Well-structured but natural
- Engaging and informative
- Appropriate for the audience

Extraction level: {extraction_level}

{conversation_context}

{additional_context}"""

    def _get_analysis_system_prompt(self) -> str:
        """
        System prompt for analysis requests - comparative and detailed.
        
        Returns:
            System prompt for analysis
        """
        return """You are an analytical assistant that breaks down topics thoroughly.

When responding to analysis requests:
- Provide thorough, balanced analysis
- Compare different perspectives when relevant
- Use structured sections only if helpful
- Support claims with reasoning
- Format clearly but naturally
- Avoid over-formatting

Provide analysis that is:
- Comprehensive and balanced
- Well-reasoned
- Clearly structured
- Practical and actionable

Extraction level: {extraction_level}

{conversation_context}

{additional_context}"""

    def _get_howto_system_prompt(self) -> str:
        """
        System prompt for how-to/guide requests - step-by-step but natural.
        
        Returns:
            System prompt for how-to guides
        """
        return """You are a helpful guide writer that provides clear instructions.

When responding to how-to requests:
- Use numbered steps for procedures
- Include necessary code examples in ```language blocks
- Explain why each step matters
- Provide warnings or tips when helpful
- Format steps clearly but naturally
- Skip unnecessary decoration

Provide guides that are:
- Easy to follow
- Complete without being verbose
- Well-paced and clear
- Practical and actionable

Extraction level: {extraction_level}

{conversation_context}

{additional_context}"""

    def _get_default_system_prompt(self) -> str:
        """
        Default system prompt - natural and conversational.
        
        Returns:
            System prompt for general questions
        """
        return """You are a helpful, knowledgeable assistant.

When responding:
- Be clear and natural
- Use markdown formatting when appropriate
- Organize information logically
- Use headers, lists, and emphasis only when helpful
- Avoid unnecessary structure
- Format like a natural conversation

Write responses that are:
- Clear and concise
- Well-organized
- Helpful and relevant
- Easy to read

Extraction level: {extraction_level}

{conversation_context}

{additional_context}"""
    
    def setup_chain(self):
        """
        Setup the LangChain chain with intent-based system prompts.
        
        Uses RunnableLambda to detect intent and select appropriate system prompt at runtime.
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{question}")
        ])
        
        # Chain with dynamic system prompt injection based on detected intent
        self.chain = (
            {
                "question": RunnablePassthrough(),
                "conversation_context": RunnablePassthrough(),
                "additional_context": RunnablePassthrough(),
                "extraction_level": RunnableLambda(lambda _: self._format_extraction_level()),
                # Dynamically detect intent and select appropriate system prompt
                "system_prompt": RunnableLambda(lambda x: self._get_system_prompt(
                    self._detect_intent(x.get("question", ""))
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
    
    def _format_response(self, text: str, intent: str) -> str:
        """
        Format response based on detected intent.
        
        This is lightweight formatting that respects the LLM's natural output
        while ensuring code blocks are properly formatted when present.
        
        Args:
            text: The raw response from the model
            intent: The detected intent
            
        Returns:
            Properly formatted response
        """
        if not text or not text.strip():
            return text
        
        # For code intent, ensure code blocks have proper formatting
        if intent == 'code':
            text = self._ensure_code_blocks(text)
        
        # General cleanup - remove any accidentally double-wrapped code blocks
        text = self._clean_code_blocks(text)
        
        return text
    
    def _ensure_code_blocks(self, text: str) -> str:
        """
        Ensure code blocks in responses have proper language identifiers.
        
        Fixes common issues like:
        - ``` without language identifier
        - Incorrectly formatted code blocks
        
        Args:
            text: Response text that may contain code blocks
            
        Returns:
            Response with properly formatted code blocks
        """
        # Find all code blocks
        lines = text.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for opening code fence
            if line.strip().startswith('```'):
                fence = line.strip()
                language = fence[3:].strip()
                
                # If no language specified, try to detect it
                if not language:
                    # Look ahead for language indicators
                    code_lines = []
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith('```'):
                        code_lines.append(lines[j])
                        j += 1
                    
                    language = self._detect_language(code_lines) if code_lines else 'plaintext'
                
                result.append(f"```{language}")
                i += 1
                
                # Copy code content until closing fence
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    result.append(lines[i])
                    i += 1
                
                # Add closing fence
                if i < len(lines):
                    result.append(lines[i])
                    i += 1
            else:
                result.append(line)
                i += 1
        
        return '\n'.join(result)
    
    def _clean_code_blocks(self, text: str) -> str:
        """
        Clean up code formatting issues.
        
        Args:
            text: Response text
            
        Returns:
            Cleaned response
        """
        # Remove double code fence markers (``` followed immediately by ```)
        text = re.sub(r'```\s*```', '```', text)
        
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        return text
    
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
