# tts.py
import pyttsx3
import json

class TTSModule:
    """文本转语音模块（使用pyttsx3）"""

    def __init__(self):
        self.engine = pyttsx3.init()
        self._setup()

    def _setup(self):
        """初始化参数设置"""
        self.engine.setProperty('rate', 150)    # 语速
        self.engine.setProperty('volume', 1.0)   # 音量

    def _extract_text(self, response: str) -> str:
        """
        预处理响应内容：
        - 如果是JSON，提取"message"字段
        - 如果不是JSON，直接返回文本
        """
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "message" in data:
                return data["message"]
            else:
                return response
        except (json.JSONDecodeError, TypeError):
            return response

    def speak(self, response: str):
        """
        朗读LLM返回的response
        :param response: LLM返回的内容（可能是文本，也可能是JSON字符串）
        """
        text = self._extract_text(response)
        print(f"TTS Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, response: str, file_path: str):
        """
        保存语音到文件
        :param response: LLM返回的内容
        :param file_path: 保存文件路径
        """
        text = self._extract_text(response)
        print(f"TTS Saving to file: {file_path}")
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()
