# client/strategies/local_strategy.py
import json
import asyncio
import re
from typing import List, Dict, Any, Optional

from .base import BaseStrategy
from ..llm import ChatEngine, MODEL_FILE
from ..speech.tts import TTSModule
from ..speech.asr import ASRModule

def clean_payload(payload):
    # 遍历 payload 的所有键值对，移除值为 None 的键
    return {key: value for key, value in payload.items() if value is not None}

class LocalLLMStrategy(BaseStrategy):
    """
    用本地 LlamaCpp(Qwen2) 推理。
    逻辑：
        1️⃣ 把用户 query 喂给 ChatEngine(本地模型) -> str
        2️⃣ 解析返回；按约定如果 message.type == "tool" 就调 MCP
        3️⃣ 若还有 follow-up，再回到 1️⃣
    """
    def __init__(self, mcp):
        super().__init__(mcp)
        self.engine = ChatEngine(MODEL_FILE)
        self.tts = TTSModule()
        self.asr = ASRModule()

    async def chat_loop(self) -> None:
        print("💬 进入本地 LLM 对话循环 (quit 退出)")
        while True:
            # query = input("\nQuery: ")
            print("🎙️正在监听... ")
            # 自动开始监听
            # query = self.asr.listen_and_transcribe()
            query = self.asr.transcribe_mic(chunk_length_s=5)
            print(f"📝监听结果: {query} ")
            if query.lower() == "quit":
                break
            await self._single_round(query)

    # ----------------- helpers -----------------
    @staticmethod
    def _safe_json(txt: str) -> Optional[Dict[str, Any]]:
        # 移除潜在的无关字符（如 'json' 或多余的符号），只保留有效的 JSON 部分
        # txt = re.sub(r"^\s*(json|```|<\s*json.*?>)*", "", txt)  # 清除开头的 `json` 或其他无关文本
        # txt = re.sub(r"\s*```", "", txt)  # 去掉多余的反引号
        txt = re.sub(r'}$', '', txt)  # 修正多余的右括号后的数据
        print(f"txt:\n{txt}")

        # 如果字符串中包含非法字符或没有形成有效的 JSON，返回 None
        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            print(f"JSON 解码错误: {e}")
            return None

    async def _single_round(self, query: str) -> None:
        reply = self.engine.ask(query)      # <-- 同步返回 str     
        payload = self._safe_json(reply)
        print(f'payload:\n{payload}')
        if payload:
            self.tts.speak(payload["message"])

        # 情形 A：模型直接给自然语言
        if not payload or payload.get("type") != "tool":
            print("\n🔊 回复：", reply)
            self.tts.speak(payload)
            return

        # 情形 B：需要调工具
        payload["arguments"] = clean_payload(payload["arguments"])
        print(f"📞 本地 LLM 要调用 {payload['name']} {payload['arguments']}")
        result = await self.mcp.call_tool(payload["name"], payload["arguments"])
        print(f"✅ 工具返回：{result}")

        # 把工具返回再丢回模型，让它生成最终答复
        follow_up = self.engine.ask('rool: '+result)
        self.tts.speak(str(follow_up))
        print("\n🔊 回复：", follow_up)
