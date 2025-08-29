#!/usr/bin/env python3
"""
Wake Word Detector Module
Handles wake word detection using OpenWakeWord
"""

import time
from threading import Thread, Event
from openwakeword.model import Model as WakeWordModel


class WakeWordDetector:
    def __init__(self, wake_words=None, confidence_threshold=0.5):
        self.wake_words = wake_words or ["alexa", "hey_jarvis"]
        self.confidence_threshold = confidence_threshold
        
        # Initialize wake word model
        print("Loading wake word model...")
        self.wake_model = WakeWordModel(
            wakeword_models=self.wake_words,
            inference_framework="onnx"
        )
        
        # State management
        self.wake_detected = Event()
        self.running = True
        self.detection_thread = None
        
    def start_detection(self, audio_manager):
        """Start wake word detection thread"""
        self.audio_manager = audio_manager
        self.detection_thread = Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        print("Wake word detection started. Say 'computer' or 'alexa'...")
        
    def _detection_loop(self):
        """Main detection loop running in thread"""
        while self.running:
            try:
                audio_data = self.audio_manager.get_wake_audio()
                if audio_data is not None:
                    # Check for wake word
                    prediction = self.wake_model.predict(audio_data)

                    # Check if any wake word was detected
                    for wake_word, confidence in prediction.items():
                        if confidence > self.confidence_threshold:
                            print(f"\n🎯 Wake word '{wake_word}' detected! (confidence: {confidence:.2f})")
                            self.wake_detected.set()
                            break

            except Exception as e:
                print(f"Wake word detection error: {e}")

            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
            
    def is_wake_detected(self):
        """Check if wake word was detected and clear the event"""
        if self.wake_detected.is_set():
            self.wake_detected.clear()
            return True
        return False
        
    def stop(self):
        """Stop wake word detection"""
        self.running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
