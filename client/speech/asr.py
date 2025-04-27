import pyaudio
import numpy as np
import time
from transformers import pipeline
from transformers.pipelines.audio_utils import ffmpeg_microphone_live

class ASRModule:
    """语音识别模块（使用Whisper）"""

    def __init__(self, model_id: str = "openai/whisper-tiny.en", device: str = "cpu", chunk_length_s: float = 1.0):
        self.model_id = model_id
        self.device = device
        self.chunk_length_s = chunk_length_s  # 每次处理的音频块时间长度（秒）
        self.transcriber = self._load_model()
        self.sample_rate = 16000  # 采样率
        self.chunk_size = int(self.sample_rate * self.chunk_length_s)  # 每个音频块的大小（样本点数）
        self.silence_threshold = 500  # 静音阈值（可调整）
        self.silence_duration = 5  # 静音持续时间（秒）

    def _load_model(self):
        """加载Whisper模型"""
        print(f"Loading ASR model: {self.model_id} on {self.device}...")
        return pipeline("automatic-speech-recognition", model=self.model_id, device=0 if self.device == "cuda" else -1)

    def transcribe_mic(self, chunk_length_s: float) -> str:
        """ Transcribe the audio from a microphone """
        # global transcriber
        sampling_rate = self.transcriber.feature_extractor.sampling_rate
        mic = ffmpeg_microphone_live(
            sampling_rate=sampling_rate,
            chunk_length_s=chunk_length_s,
            stream_chunk_s=chunk_length_s,
        )

        result = ""
        for item in self.transcriber(mic):
            result = item["text"]
            if not item["partial"][0]:
                break
        return result.strip()

    # def _get_audio_data(self):
    #     """获取音频流数据"""
    #     stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
    #                                       channels=1,
    #                                       rate=self.sample_rate,
    #                                       input=True,
    #                                       frames_per_buffer=self.chunk_size)
    #     return stream

    # def _is_silent(self, audio_data):
    #     """判断音频数据是否静音"""
    #     rms = np.sqrt(np.mean(np.square(np.frombuffer(audio_data, dtype=np.int16))))
    #     return rms < self.silence_threshold

    # def listen_and_transcribe(self):
    #     """监听麦克风并转录"""
    #     stream = self._get_audio_data()
    #     print("Listening... Start speaking now!")

    #     frames = []
    #     silence_start_time = time.time()  # 记录开始静音的时间

    #     result = ""
    #     while True:
    #         audio_data = stream.read(self.chunk_size)
    #         frames.append(audio_data)

    #         if self._is_silent(audio_data):
    #             if time.time() - silence_start_time > self.silence_duration:
    #                 print("Silence detected. Stopping...")
    #                 break
    #         else:
    #             silence_start_time = time.time()  # 用户开始说话，重置计时器

    #         # 转录每个音频块
    #         audio_chunk = b''.join(frames)
    #         result = self.transcribe_from_audio(audio_chunk)

    #     # 关闭音频流
    #     stream.stop_stream()
    #     stream.close()

    #     return result.strip()

    # def transcribe_from_audio(self, audio_data: bytes):
    #     """将音频数据转换为文字"""
    #     print("Transcribing audio...")

    #     # 直接传递音频数据进行转录（无需保存为文件）
    #     result = self.transcriber(audio_data)
    #     return result["text"]
