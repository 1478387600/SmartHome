import argparse
import os
from llm.chat_engine import ChatEngine
from speech.asr import ASRModule
from speech.tts import TTSModule

# 简称 -> 完整模型文件名的映射
MODEL_MAP = {
    "qwen": "qwen2.5-1.5b-instruct-fp16.gguf",
    "mistral": "mistral-7b-instruct.gguf",
    "tinyllama": "tinyllama-1.1b-chat.gguf",
}

def parse_args():
    parser = argparse.ArgumentParser(
        description="LLaMA GPT Chat with ASR and TTS",
        usage="python llm_chat.py --model [qwen|mistral|tinyllama]"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="模型简称，比如 qwen、mistral、tinyllama",
    )
    args = parser.parse_args()

    if args.model not in MODEL_MAP:
        print(f"❌ 无效模型名 '{args.model}'。请选择: {list(MODEL_MAP.keys())}")
        exit(1)

    return args

def main():
    args = parse_args()

    # 根据简称找到完整路径
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    model_file = MODEL_MAP[args.model]
    model_path = os.path.join(model_dir, model_file)

    # 检查模型文件是否存在
    if not os.path.isfile(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        exit(1)

    print(f"✅ 正在使用模型: {args.model} ({model_file})")

    # 初始化各个模块
    chat_engine = ChatEngine(model_path=model_path)  # 要把 model_path传进去
    asr = ASRModule()
    tts = TTSModule()

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
