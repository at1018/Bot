"""Base class for LLM providers."""
from abc import ABC, abstractmethod
from random import random
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
    
    def setup_chain(self):
        """Setup the LangChain prompt and chain."""
        system_template = """You are a helpful chatbot assistant specialized in providing structured, well-formatted responses.

## CRITICAL: CODE FORMATTING RULES

### For ALL Code Requests (Python, JavaScript, Java, etc.):

**MANDATORY FORMAT:**
1. Write the complete code with PROPER INDENTATION (use 4 spaces for Python)
2. NO triple backticks - just plain code with proper formatting
3. Each section clearly organized
4. Add blank line after code
5. Then provide explanation sections with headers

**INDENTATION IS CRITICAL:**
- Python: 4 spaces per indentation level
- JavaScript: 2 spaces per indentation level
- Java: 4 spaces per indentation level

**CODE MUST INCLUDE:**
- Proper indentation throughout
- Clear variable names
- Comments for complex logic
- Error handling

### Code Format TEMPLATE (NO backticks):

import random

def guess_the_number():
    Main game function with proper indentation.
    secret = random.randint(1, 100)
    guesses = 0
    
    print("Welcome to Guess the Number!")
    
    while True:
        try:
            guess = int(input("Enter your guess: "))
            guesses += 1
            
            if guess < secret:
                print("Too low! Try again.")
            elif guess > secret:
                print("Too high! Try again.")
            else:
                print(f"Correct! You guessed in {{guesses}} attempts!")
                break
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    guess_the_number()

**What it does:**
Brief explanation here.

**How it works:**
- Step 1: Description
- Step 2: Description
- Step 3: Description

**Example usage:**
Show how to run and expected output.

### GENERAL RULES FOR ALL RESPONSES:
- Code should be plain text with proper indentation (NO markdown code blocks)
- All code must have proper indentation
- After code sections, always provide explanation
- Use headers (##, ###) to structure response
- Use bullet points for lists
- Use **bold** for important terms

## EXTRACTION LEVEL: {extraction_level}

**REMEMBER:** Plain code with proper indentation is ESSENTIAL. NO triple backticks. Format ALL code responses this way.

{conversation_context}

{additional_context}"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", "{question}")
        ])
        
        self.chain = (
            {
                "question": RunnablePassthrough(),
                "conversation_context": RunnablePassthrough(),
                "additional_context": RunnablePassthrough(),
                "extraction_level": RunnableLambda(lambda _: self._format_extraction_level()),
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
        Post-process response to format code with proper indentation and structure.
        Does NOT wrap in markdown code blocks - just ensures proper formatting.
        """
        # If already has code blocks, remove them
        text = text.replace('```python\n', '')
        text = text.replace('```javascript\n', '')
        text = text.replace('```java\n', '')
        text = text.replace('```\n', '')
        text = text.replace('```', '')
        
        return text
