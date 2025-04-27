# callback.py
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Any, Dict, List

class StreamingCustomCallbackHandler(StreamingStdOutCallbackHandler):
    """自定义流式输出的Callback"""

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        print("<LLM Started>")

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        print("<LLM Ended>")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        print(f"{token}", end="")
