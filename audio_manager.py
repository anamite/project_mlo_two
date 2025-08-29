#!/usr/bin/env python3
"""
Audio Manager Module
Handles audio input/output operations including recording, playback, and TTS
"""

import numpy as np
import sounddevice as sd
import queue
import sys
from kittentts import KittenTTS


class AudioManager:
    def __init__(self, samplerate=16000):
        self.samplerate = samplerate
        self.audio_queue = queue.Queue()
        self.wake_queue = queue.Queue()
        
        # Initialize TTS model
        print("Loading TTS model...")
        self.tts_model = KittenTTS("KittenML/kitten-tts-nano-0.2")
        
        # TTS voices
        self.voices = [
            'expr-voice-2-m', 'expr-voice-2-f', 'expr-voice-3-m', 'expr-voice-3-f',
            'expr-voice-4-m', 'expr-voice-4-f', 'expr-voice-5-m', 'expr-voice-5-f'
        ]
        self.current_voice = 'expr-voice-2-m'
        
    def set_voice(self, voice):
        """Set the TTS voice"""
        if voice in self.voices:
            self.current_voice = voice
        else:
            print(f"Warning: Voice '{voice}' not available. Using default.")
    
    def play_beep(self, frequency=800, duration=0.2):
        """Play a beep tone to indicate activation"""
        try:
            sample_rate = 24000
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = 0.3 * np.sin(frequency * 2 * np.pi * t)
            sd.play(wave, samplerate=sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Beep error: {e}")

    def speak(self, text):
        """Convert text to speech and play it"""
        try:
            print(f"🔊 Speaking: {text}")
            audio = self.tts_model.generate(text, voice=self.current_voice)
            sd.play(audio, samplerate=24000)
            sd.wait()  # Wait until audio finishes playing
        except Exception as e:
            print(f"TTS Error: {e}")

    def wake_word_callback(self, indata, frames, time, status):
        """Callback for wake word detection"""
        if status:
            print(status, file=sys.stderr)

        # Convert to int16 for openWakeWord
        audio_int16 = np.frombuffer(indata, dtype=np.float32) * 32767
        audio_int16 = audio_int16.astype(np.int16)
        self.wake_queue.put(audio_int16)

    def command_callback(self, indata, frames, time, status):
        """Callback for command recording (VOSK)"""
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def get_wake_audio(self):
        """Get audio data for wake word detection"""
        if not self.wake_queue.empty():
            return self.wake_queue.get_nowait()
        return None

    def get_command_audio(self, timeout=0.1):
        """Get audio data for command recognition"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
