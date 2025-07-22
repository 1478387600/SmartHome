"""
client/llm/chat_engine.py - LLM Chat Engine Implementation

This module implements the core chat engine that handles:
- LLM model initialization
- Prompt construction
- Response generation

Key Features:
- Abstracts LLM model interaction
- Handles prompt templating
- Manages conversation chains

Location: client/llm/chat_engine.py (relative to project root)

Dependencies:
- .model: LLM model wrapper
- .prompt: Prompt construction utilities
"""
from .model import LLMModel
from .prompt import PromptBuilder

class ChatEngine:
    """
    Core chat engine for managing LLM question-answering chains.
    
    Responsibilities:
    - Initializes and manages LLM model instance
    - Constructs prompts for queries
    - Executes question-answering chains
    - Returns formatted responses
    
    Usage:
        engine = ChatEngine(model_path="path/to/model.gguf")
        response = engine.ask("What is the weather?")
    """

    def __init__(self, model_path: str):
        """
        Initialize chat engine with specified LLM model.
        
        Args:
            model_path: Path to GGUF model file
        """
        self.model = LLMModel(model_path).get_llm()

    def ask(self, question: str) -> str:
        """
        Process a question through the LLM and return response.
        
        Args:
            question: Input query string
            
        Returns:
            str: Generated response from LLM
            
        Steps:
            1. Build prompt template
            2. Create processing chain
            3. Invoke chain with question
            4. Return response
        """
        prompt = PromptBuilder.build_prompt(question)
        chain = prompt | self.model
        response = chain.invoke({"question": question}, config={})
        return response
