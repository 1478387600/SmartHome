"""
client/llm_chat.py - LLM Chat Interface with ASR/TTS Support

This module provides a command-line interface for interacting with LLM models,
supporting both text and voice input/output through ASR (Automatic Speech Recognition)
and TTS (Text-to-Speech) modules.

Key Features:
- Supports multiple LLM models (Qwen, Mistral, TinyLLaMA)
- Interactive text and voice chat modes
- Automatic model file path resolution

Location: client/llm_chat.py (relative to project root)

Dependencies:
- llm.chat_engine: Core LLM chat functionality
- speech.asr: Speech recognition module
- speech.tts: Text-to-speech module
"""

import argparse
import os
from llm.chat_engine import ChatEngine
from speech.asr import ASRModule
from speech.tts import TTSModule

# Model name shorthand -> full model filename mapping
MODEL_MAP = {
    "qwen": "qwen2.5-1.5b-instruct-fp16.gguf",
    "mistral": "mistral-7b-instruct.gguf",
    "tinyllama": "tinyllama-1.1b-chat.gguf",
}

def parse_args():
    """
    Parse command line arguments for LLM chat interface.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
        
    Raises:
        SystemExit: If invalid model name is provided
    """
    parser = argparse.ArgumentParser(
        description="LLaMA GPT Chat with ASR and TTS",
        usage="python llm_chat.py --model [qwen|mistral|tinyllama]"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model shorthand name (qwen, mistral, or tinyllama)",
    )
    args = parser.parse_args()

    if args.model not in MODEL_MAP:
        print(f"❌ Invalid model name '{args.model}'. Please choose from: {list(MODEL_MAP.keys())}")
        exit(1)

    return args

def main():
    """
    Main entry point for LLM chat interface.
    
    Handles:
    - Model file path resolution
    - Module initialization
    - Interactive chat loop
    - Mode selection (text/voice input)
    """
    args = parse_args()

    # Resolve full model path from shorthand name
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    model_file = MODEL_MAP[args.model]
    model_path = os.path.join(model_dir, model_file)

    # Verify model file exists
    if not os.path.isfile(model_path):
        print(f"❌ Model file not found: {model_path}")
        exit(1)

    print(f"✅ Using model: {args.model} ({model_file})")

    # Initialize all modules
    chat_engine = ChatEngine(model_path=model_path)  # Pass model_path to chat engine
    asr = ASRModule()  # Automatic Speech Recognition
    tts = TTSModule()  # Text-to-Speech

    mode = input("Choose mode: (1) Text input (2) Audio input : ")

    while True:
        if mode == "2":
            audio_path = input("\nEnter audio file path (or type 'exit'): ")
            if audio_path.lower() == 'exit':
                break
            question = asr.transcribe(audio_path)
            print(f"Transcribed: {question}")
        else:
            question = input("\nPlease enter your question (or type 'exit' to quit): ")
            if question.lower() == 'exit':
                break

        if question.strip():
            print(f"\nYou asked: {question}")
            response = chat_engine.ask(question)
            print(f"\nResponse: {response}")

            tts.speak(str(response))

if __name__ == "__main__":
    main()
