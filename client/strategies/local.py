"""
client/strategies/local.py - Local LLM Strategy Implementation

This module implements the local LLM strategy using Qwen2 model via LlamaCpp.
It handles voice input/output and processes queries through the local model.

Key Features:
- Local LLM inference with Qwen2
- Voice input via ASR
- Voice output via TTS
- Tool call integration with MCP

Location: client/strategies/local.py (relative to project root)

Dependencies:
- .base: Base strategy interface
- ..llm: Chat engine and model
- ..speech: TTS and ASR modules
"""
import json
import asyncio
import re
from typing import List, Dict, Any, Optional

from .base import BaseStrategy
from ..llm import ChatEngine, MODEL_FILE
from ..speech.tts import TTSModule
from ..speech.asr import ASRModule

def clean_payload(payload):
    """Remove None values from payload dictionary."""
    return {key: value for key, value in payload.items() if value is not None}

class LocalLLMStrategy(BaseStrategy):
    """
    Local LLM strategy using Qwen2 model via LlamaCpp.
    
    Processing flow:
    1. Feed user query to ChatEngine (local model) -> str response
    2. Parse response - if message.type == "tool" call MCP
    3. If follow-up needed, return to step 1
    
    Supports both text and voice interaction modes.
    """

    def __init__(self, mcp):
        """
        Initialize local LLM strategy.
        
        Args:
            mcp: MCPClient instance for tool execution
        """
        super().__init__(mcp)
        self.engine = ChatEngine(MODEL_FILE)
        self.tts = TTSModule()
        self.asr = ASRModule()

    async def chat_loop(self) -> None:
        """Main chat interaction loop with voice input."""
        print("💬 Entering local LLM chat loop (type 'quit' to exit)")
        while True:
            print("🎙️ Listening...")
            query = self.asr.transcribe_mic(chunk_length_s=5)
            print(f"📝 Transcription: {query}")
            if query.lower() == "quit":
                break
            await self._single_round(query)

    # ----------------- Helper Methods -----------------
    # @staticmethod
    # def _safe_json(txt: str) -> Optional[Dict[str, Any]]:
    #     """
    #     Safely parse JSON string, cleaning invalid characters.
        
    #     Args:
    #         txt: Input string potentially containing JSON
            
    #     Returns:
    #         Parsed JSON dict or None if invalid
    #     """
    #     # Clean potential invalid JSON prefixes/suffixes
    #     txt = re.sub(r'}$', '', txt)  # Fix trailing braces
    #     # print(f"Cleaned text:\n{txt}")

    #     try:
    #         return json.loads(txt)
    #     except json.JSONDecodeError as e:
    #         print(f"JSON decode error: {e}")
    #         return None
    @staticmethod
    def _safe_json(txt: str) -> Optional[Dict[str, Any]]:
        """
        Safely parse the first JSON object found in a string, ignoring leading/trailing garbage.

        Args:
            txt: Input string potentially containing JSON.

        Returns:
            Parsed JSON dict (first object) or None if invalid/not found.
        """
        # Find the first '{'
        start = txt.find('{')
        if start == -1:
            # no JSON object start
            return None

        txt = txt[start:]

        decoder = json.JSONDecoder()
        try:
            # raw_decode returns (obj, end_index)
            obj, end = decoder.raw_decode(txt)
            return obj
        except json.JSONDecodeError as e:
            # Could not decode a full object from txt
            print(f"JSON decode error: {e}")
            return None

    async def _single_round(self, query: str) -> None:
        """
        Process a single query-response cycle.
        
        Args:
            query: User input query string
        """
        reply = self.engine.ask(query)
        # print(f'reply:\n{reply}')
        payload = self._safe_json(reply)
        print(f'Payload:\n{payload}')
        # self.tts.speak(payload["message"])
        if payload is not None:
            self.tts.speak(payload["message"])
            pass

        # Case A: Direct natural language response
        if not payload or payload.get("type") != "tool":
            print("\n🔊 Response:", reply)
            if payload:
                self.tts.speak(payload["message"])
            return

        # Case B: Tool call required
        payload["arguments"] = clean_payload(payload["arguments"])
        print(f"📞 Local LLM requesting tool call: {payload['name']} {payload['arguments']}")
        result = await self.mcp.call_tool(payload["name"], payload["arguments"])
        print(f"✅ Tool response: {result}")

        # Feed tool result back to model for final response
        follow_up = self.engine.ask('tool: '+result)
        payload = self._safe_json(follow_up)
        if payload:
            self.tts.speak(str(payload["message"]))
        print("\n🔊 Final response:", follow_up)
