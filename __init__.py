#!/usr/bin/env python3
"""
Voice Assistant Package
A modular voice assistant with wake word detection, speech recognition, and AI integration
"""

from .voice_assistant import VoiceAssistant
from .audio_manager import AudioManager
from .wake_word_detector import WakeWordDetector
from .speech_recognizer import SpeechRecognizer
from .command_processor import CommandProcessor
from .command_executor import CommandExecutor
from .api_client import APIClient
from .database_manager import DatabaseManager, UserSettingsManager

__version__ = "1.0.0"
__author__ = "Voice Assistant Team"

__all__ = [
    "VoiceAssistant",
    "AudioManager", 
    "WakeWordDetector",
    "SpeechRecognizer",
    "CommandProcessor",
    "CommandExecutor",
    "APIClient",
    "DatabaseManager",
    "UserSettingsManager"
]
