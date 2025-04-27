# asr.py
from transformers import pipeline

class ASRModule:
    """语音识别模块（使用Whisper）"""

    def __init__(self, model_id: str = "openai/whisper-tiny.en", device: str = "cpu"):
        self.model_id = model_id
        self.device = device
        self.transcriber = self._load_model()

    def _load_model(self):
        print(f"Loading ASR model: {self.model_id} on {self.device}...")
        return pipeline("automatic-speech-recognition", model=self.model_id, device=0 if self.device == "cuda" else -1)

    def transcribe(self, audio_path: str) -> str:
        """
        将音频文件转为文字
        :param audio_path: 音频文件路径（如wav, mp3）
        :return: 转写的文本内容
        """
        print(f"Transcribing audio: {audio_path}")
        result = self.transcriber(audio_path)
        return result["text"]
