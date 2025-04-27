# model.py
from langchain_community.llms import LlamaCpp
from .callback import StreamingCustomCallbackHandler
from .config import MODEL_FILE
from langchain.callbacks.manager import CallbackManager

class LLMModel:
    """管理LlamaCpp模型的加载"""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.callback_manager = CallbackManager([StreamingCustomCallbackHandler()])
        self.llm = self._load_model()

    def _load_model(self) -> LlamaCpp:
        return LlamaCpp(
            model_path=self.model_path,
            n_gpu_layers=-1,
            n_ctx=1024,
            temperature=0.2,
            top_p=0.8,
            model_kwargs={"chat_format": "qwen2"},
            streaming=True,
        )

    def get_llm(self) -> LlamaCpp:
        return self.llm
