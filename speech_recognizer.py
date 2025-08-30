#!/usr/bin/env python3
"""
Speech Recognizer Module
Handles speech recognition using VOSK
"""

import json
import time
from vosk import Model, KaldiRecognizer


class SpeechRecognizer:
    def __init__(self, model_lang="en-us", samplerate=16000):
        self.samplerate = samplerate
        
        # Initialize VOSK model
        print("Loading speech recognition model...")
        self.vosk_model = Model(lang=model_lang)
        
    def recognize_command(self, audio_manager, listening_event, max_silence_duration=3.0):
        """Listen for and recognize a command"""
        print("🎤 Listening for command... (speak now)")

        # Create recognizer
        rec = KaldiRecognizer(self.vosk_model, self.samplerate)

        command_text = ""
        silence_start = None

        while listening_event.is_set():
            try:
                data = audio_manager.get_command_audio(timeout=0.1)
                if data is None:
                    continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result['text']:
                        command_text = result['text']
                        print(f"📝 Final: {command_text}")
                        break
                else:
                    partial = json.loads(rec.PartialResult())
                    if partial['partial']:
                        print(f"📝 Partial: {partial['partial']}", end='\r')
                        silence_start = None  # Reset silence timer on speech
                    else:
                        # No speech detected
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > max_silence_duration:
                            print(f"\n⏰ Silence timeout, processing: '{command_text}'")
                            break

            except Exception as e:
                print(f"Command recognition error: {e}")
                break

        return command_text
