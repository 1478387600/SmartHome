"""
client/speech/asr.py - Automatic Speech Recognition Module

This module implements speech-to-text functionality using Whisper models,
providing real-time transcription from microphone input.

Key Features:
- Whisper model integration
- Real-time audio streaming
- Microphone input handling
- Configurable chunk processing

Location: client/speech/asr.py (relative to project root)

Dependencies:
- transformers: Whisper model pipeline
- pyaudio: Audio stream handling (optional)
- numpy: Audio processing (optional)
"""
import pyaudio
import numpy as np
import time
from transformers import pipeline
from transformers.pipelines.audio_utils import ffmpeg_microphone_live

class ASRModule:
    """
    Automatic Speech Recognition module using Whisper models.
    
    Provides real-time speech-to-text transcription with configurable:
    - Model size (tiny, base, small, medium, large)
    - Processing chunk size
    - Silence detection thresholds
    
    Usage:
        asr = ASRModule(model_id="openai/whisper-base.en")
        text = asr.transcribe_mic(5.0)  # 5 second chunks
    """

    def __init__(self, model_id: str = "openai/whisper-tiny.en", device: str = "cpu", chunk_length_s: float = 1.0):
        """
        Initialize ASR module.
        
        Args:
            model_id: Whisper model identifier
            device: Processing device ('cpu' or 'cuda')
            chunk_length_s: Audio chunk duration in seconds
        """
        self.model_id = model_id
        self.device = device
        self.chunk_length_s = chunk_length_s  # Audio chunk duration (seconds)
        self.transcriber = self._load_model()
        self.sample_rate = 16000  # Sample rate (Hz)
        self.chunk_size = int(self.sample_rate * self.chunk_length_s)  # Samples per chunk
        self.silence_threshold = 500  # RMS threshold for silence detection
        self.silence_duration = 5  # Silence duration to stop (seconds)

    def _load_model(self):
        """Load and initialize Whisper ASR model."""
        print(f"Initializing ASR model: {self.model_id} on {self.device}...")
        return pipeline("automatic-speech-recognition", 
                      model=self.model_id, 
                      device=0 if self.device == "cuda" else -1)

    def transcribe_mic(self, chunk_length_s: float) -> str:
        """
        Transcribe live microphone input.
        
        Args:
            chunk_length_s: Duration of audio chunks to process
            
        Returns:
            str: Transcribed text
            
        Note:
            Uses ffmpeg for efficient live audio streaming
        """
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
