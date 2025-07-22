"""
client/llm/prompt.py - LLM Prompt Construction Utilities

This module handles the construction of chat prompts for LLM interactions,
combining system instructions with user queries.

Key Features:
- System message templating
- User question formatting
- Chat prompt assembly

Location: client/llm/prompt.py (relative to project root)

Dependencies:
- langchain.prompts: Chat prompt templates
- langchain.schema: Message types
- .config: System message template
"""

from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from .config import SYSTEM_MESSAGE


class PromptBuilder:
    """
    Utility class for constructing LLM chat prompts.

    Responsibilities:
    - Combines system instructions with user queries
    - Formats messages for LLM consumption
    - Maintains consistent prompt structure

    Usage:
        prompt = PromptBuilder.build_prompt("How's the weather?")
    """

    @staticmethod
    def build_prompt(question: str) -> ChatPromptTemplate:
        """
        Construct a chat prompt from system message and user question.

        Args:
            question: User input query string

        Returns:
            ChatPromptTemplate: Formatted prompt containing:
                - System instructions
                - User question
        """
        return ChatPromptTemplate.from_messages(
            [SystemMessage(content=SYSTEM_MESSAGE), HumanMessage(content=question)]
        )
