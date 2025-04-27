# prompt.py
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from .config import SYSTEM_MESSAGE

class PromptBuilder:
    """构建Prompt"""

    @staticmethod
    def build_prompt(question: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_MESSAGE),
            HumanMessage(content=question)
        ])
