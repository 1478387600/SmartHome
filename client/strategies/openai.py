# client/strategies/openai_strategy.py
import os
import sys
import json
import asyncio
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

from .base import BaseStrategy
from client.speech.tts import TTSModule
from client.speech.asr import ASRModule

load_dotenv()


class OpenAIStrategy(BaseStrategy):
    def __init__(self, mcp):
        super().__init__(mcp)
        self.client = OpenAI()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.tts = TTSModule()
        self.asr = ASRModule()

    # --------- Internal Helpers ---------
    async def _build_messages(
        self, query: str, tools: List[Dict[str, Any]], devices: List[dict], sensors: List[dict]
    ) -> List[Dict[str, Any]]:
        sys_prompt = (
            "You are a smart home assistant. User queries are meant to control various home devices.\n"
            "Your responses are divided into two typs, answers and tool calls. An answer contain only natural language while tool calls don't.\n"
            "You MUST use provided tool functions to perform actions instead of answering directly.\n"
            "Always preserve the full intent of the user query and respond with the appropriate tool call.\n"
            "If you still want to call the tools, set the finish_reason='tool_calls'.\n"
            "If you are calling a tool in your response while the finish_reason='stop', change it to finish_reason='tool_calls'.\n"
            "If your response is based on tool calls, make sure put all the calls into one response and set the finish_reason='tool_calls'.\n"
            "If you set the finish_reason='tool_calls', don't make tool_calls.\n"
            "Your response can not be an answer before you have done all the tool calls need to finish your task given by user."
            "Put multiple tasks in one response using several tool calls.\n"
            "If the user mentions a specific device ID (e.g., bedroom_ac or kitchen_light), use the corresponding tool.\n"
            "NEVER hardcode responses or insert specific time/status values—retrieve them via tool calls.\n"
            "The user might say things like 'turn on living room TV', 'set bedroom AC to 24 degrees', or 'what’s the status of the kitchen light?'—you must respond by calling the correct function.\n"
            "For those devices can be set the values, you put all the arguments in one function call. for example {'device_id': 'living_room_ac', 'status': 'on', 'level': 20} \n"
            "You don't need to call the "
            "Do not lose user context. Preserve the full query meaning as much as possible.\n"
            "available tools and devices are below\n"
            f"{json.dumps(tools, ensure_ascii=False)}\n"
            f"{json.dumps(devices + sensors, ensure_ascii=False)}"
        )
        return [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": query},
        ]

    # --------- Main Conversation Loop ---------
    async def chat_loop(self) -> None:
        print("💬 Entering conversation loop (type quit to exit)")
        while True:
            # query = input("\nQuery: ").strip()
            print("🎙️ Listening... ")
            # Automatic start of listening
            # query = self.asr.listen_and_transcribe()  # 自动监听并转化为文字
            query = self.asr.transcribe_mic(chunk_length_s=5)
            print(f"📝 Listening result: {query} ")
            if query.lower() == "quit":
                break
            await self._single_round(query)

    async def _single_round(self, query: str) -> None:
        # Get tool list and device, sensor information
        tools = await self.mcp.list_tools()
        devices, sensors = await self.mcp.read_devices()
        
        # Building a Message
        messages = await self._build_messages(query, tools, devices, sensors)
        print(f"messages:\n{messages}")

        # First call to LLM
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": t} for t in tools],
        )
        choice = resp.choices[0]

        # If a tool call is needed
        if choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls  # Get a list of tool calls
            messages.append({
                "role": "assistant",
                "tool_calls": [{
                    'id': tool_call.id,
                    'function': {
                        'arguments': tool_call.function.arguments,
                        'name': tool_call.function.name
                    },
                    'type': 'function'
                } for tool_call in tool_calls]
            })

        # Enter tool call processing loop
        while choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            for tc in tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"📞 Calling {tc.function.name} {args}")
                # Call the corresponding tool
                result = await self.mcp.call_tool(tc.function.name, args)
                messages.append(
                    {
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tc.id,
                    }
                )
            print(f"result:\n{result}")

            # print(f"devices, sensors:\n{devices, sensors}")
            # Call LLM again
            resp = self.client.chat.completions.create(
                model=self.model, messages=messages
            )
            choice = resp.choices[0]
            print(f"choice:\n{choice}")

            # Check if LLM still needs to invoke tools
            if choice.finish_reason == "tool_calls":
                continue  # If there is a tool call, continue to loop
            
            # Text To Speech: Make sure you pass string type
            if 'message' in choice and hasattr(choice.message, 'content'):
                self.tts.speak(choice.message.content)  # Access content correctly for TTS Text To Speech

        print("\n🔊 Response:", choice.message.content)  # Print final response
