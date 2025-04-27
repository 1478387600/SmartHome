# chat_engine.py
from .model import LLMModel
from .prompt import PromptBuilder

class ChatEngine:
    """负责问答链的调用"""

    def __init__(self, model_path: str):
        self.model = LLMModel(model_path).get_llm()

    def ask(self, question: str):
        prompt = PromptBuilder.build_prompt(question)
        chain = prompt | self.model
        response = chain.invoke({"question": question}, config={})
        return response
