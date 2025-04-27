# tts.py
import pyttsx3

class TTSModule:
    """文本转语音模块（使用pyttsx3）"""

    def __init__(self):
        self.engine = pyttsx3.init()
        self._setup()

    def _setup(self):
        """可选：初始化参数设置"""
        self.engine.setProperty('rate', 150)    # 语速
        self.engine.setProperty('volume', 1.0)   # 音量

    def speak(self, text: str):
        """
        将文本朗读出来
        :param text: 需要朗读的文本
        """
        print(f"TTS Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, text: str, file_path: str):
        """
        保存语音为音频文件
        :param text: 文本内容
        :param file_path: 保存的文件路径（如output.wav）
        """
        print(f"TTS Saving to file: {file_path}")
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()
