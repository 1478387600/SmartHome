# client/strategies/local_strategy.py
import json
import asyncio
from typing import List, Dict, Any

from .base import BaseStrategy
from ..llm import ChatEngine, MODEL_FILE


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

    async def chat_loop(self) -> None:
        print("💬 进入本地 LLM 对话循环 (quit 退出)")
        while True:
            query = input("\nQuery: ")
            if query.lower() == "quit":
                break
            print(f'{query}')
            await self._single_round(query)

    # ----------------- helpers -----------------
    @staticmethod
    def _safe_json(txt: str) -> Dict[str, Any] | None:
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return None

    async def _single_round(self, query: str) -> None:
        reply = self.engine.ask(query)      # <-- 同步返回 str     
        payload = self._safe_json(reply)

        # 情形 A：模型直接给自然语言
        if not payload or payload.get("type") != "tool":
            print("\n🔊 回复：", reply)
            return

        # 情形 B：需要调工具
        print(f"📞 本地 LLM 要调用 {payload['name']} {payload['arguments']}")
        result = await self.mcp.call_tool(payload["name"], payload["arguments"])
        print(f"✅ 工具返回：{result}")

        # 把工具返回再丢回模型，让它生成最终答复
        follow_up = self.engine.ask(result)
        print("\n🔊 回复：", follow_up)
