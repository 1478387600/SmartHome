"""
client/llm/model.py - LLM Model Wrapper Implementation

This module provides a wrapper class for managing LlamaCpp model instances,
handling model loading and configuration with streaming callbacks.

Key Features:
- LlamaCpp model initialization
- GPU layer configuration
- Context window setup
- Streaming callback integration

Location: client/llm/model.py (relative to project root)

Dependencies:
- langchain_community.llms: LlamaCpp implementation
- .callback: Custom streaming callbacks
- .config: Model file path configuration
"""

from langchain_community.llms import LlamaCpp
from .callback import StreamingCustomCallbackHandler
from .config import MODEL_FILE
from langchain.callbacks.manager import CallbackManager


class LLMModel:
    """
    Wrapper class for managing LlamaCpp model instances.

    Responsibilities:
    - Handles model loading and initialization
    - Configures GPU acceleration
    - Sets up streaming callbacks
    - Provides access to model instance

    Usage:
        model = LLMModel("path/to/model.gguf")
        llm = model.get_llm()
    """

    def __init__(self, model_path: str):
        """
        Initialize LLM model wrapper.

        Args:
            model_path: Path to GGUF model file
        """
        self.model_path = model_path
        self.callback_manager = CallbackManager([StreamingCustomCallbackHandler()])
        self.llm = self._load_model()

    def _load_model(self) -> LlamaCpp:
        """
        Load and configure LlamaCpp model instance.

        Returns:
            LlamaCpp: Configured model instance with:
                - GPU acceleration
                - 1024 token context window
                - Qwen2 chat format
                - Streaming enabled
        """
        return LlamaCpp(
            model_path=self.model_path,
            n_gpu_layers=-1,  # Use all GPU layers
            n_ctx=1024,  # Context window size
            temperature=0.2,  # Creativity control
            top_p=0.8,  # Nucleus sampling
            model_kwargs={"chat_format": "qwen2"},
            streaming=True,
        )

    def get_llm(self) -> LlamaCpp:
        """
        Get the initialized LlamaCpp model instance.

        Returns:
            LlamaCpp: Ready-to-use model instance
        """
        return self.llm
