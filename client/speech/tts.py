"""
client/speech/tts.py - Text-to-Speech Module

This module provides text-to-speech functionality using pyttsx3,
converting text responses into spoken audio output.

Key Features:
- Real-time speech synthesis
- JSON response parsing
- Audio file saving
- Configurable speech parameters

Location: client/speech/tts.py (relative to project root)

Dependencies:
- pyttsx3: Cross-platform TTS engine
- json: Response parsing
"""
import pyttsx3
import json

class TTSModule:
    """
    Text-to-speech module using pyttsx3 engine.
    
    Handles:
    - Speech synthesis from text
    - JSON response parsing
    - Audio file generation
    - Speech rate/volume control
    
    Usage:
        tts = TTSModule()
        tts.speak("Hello world")  # Speak immediately
        tts.save_to_file("Hello", "output.wav")  # Save to file
    """

    def __init__(self):
        """Initialize TTS engine with default settings."""
        self.engine = pyttsx3.init()
        self._setup()

    def _setup(self):
        """Configure TTS engine parameters."""
        self.engine.setProperty('rate', 150)    # Words per minute
        self.engine.setProperty('volume', 1.0)   # Volume level (0.0-1.0)

    def _extract_text(self, response: str) -> str:
        """
        Extract text from LLM response.
        
        Args:
            response: LLM response (text or JSON string)
            
        Returns:
            str: Extracted text content
            
        Handles both:
        - Raw text responses
        - JSON responses with 'message' field
        """
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "message" in data:
                return data["message"]
            return response
        except (json.JSONDecodeError, TypeError):
            return response

    def speak(self, response: str):
        """
        Convert text to speech and play immediately.
        
        Args:
            response: LLM response (text or JSON string)
        """
        text = self._extract_text(response)
        print(f"[TTS] Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, response: str, file_path: str):
        """
        Save speech output to audio file.
        
        Args:
            response: LLM response (text or JSON string)
            file_path: Output file path (.wav, .mp3, etc)
        """
        text = self._extract_text(response)
        print(f"[TTS] Saving to {file_path}")
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()
