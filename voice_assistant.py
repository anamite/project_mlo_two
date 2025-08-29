#!/usr/bin/env python3
"""
Voice Assistant Main Module
Orchestrates all components of the voice assistant
"""

import asyncio
import sounddevice as sd
from threading import Event

from project_mlo_two.audio_manager import AudioManager
from project_mlo_two.wake_word_detector import WakeWordDetector
from project_mlo_two.speech_recognizer import SpeechRecognizer
from project_mlo_two.command_processor import CommandProcessor
from project_mlo_two.command_executor import CommandExecutor


class VoiceAssistant:
    def __init__(self, model_lang="en-us", samplerate=16000, voice="expr-voice-2-m"):
        self.samplerate = samplerate
        
        # Initialize all components
        print("Initializing voice assistant components...")
        self.audio_manager = AudioManager(samplerate)
        self.wake_word_detector = WakeWordDetector()
        self.speech_recognizer = SpeechRecognizer(model_lang, samplerate)
        self.command_processor = CommandProcessor()
        self.command_executor = CommandExecutor(self.audio_manager)
        
        # Set voice
        self.audio_manager.set_voice(voice)
        
        # State management
        self.listening_for_command = Event()
        self.running = True

        print("All models loaded successfully!")

    async def process_command_async(self, command_text):
        """Process command asynchronously"""
        if command_text.strip():
            print(f"\n📥 Processing: '{command_text}'")

            # Process with embedding model
            command, confidence, song, song_confidence = self.command_processor.process_command(command_text)

            print(f"🎯 Best match: '{command}' ({confidence:.1f}%)")
            if song:
                print(f"🎵 Song match: '{song}' ({song_confidence:.1f}%)")

            # Execute command (includes voice response)
            await self.command_executor.execute_command(command, song, command_text)
        else:
            self.audio_manager.speak("I didn't hear anything. Please try again.")

    def run(self):
        """Main assistant loop with async support"""
        async def async_main():
            try:
                print("\n" + "=" * 60)
                print("🎙️  VOICE ASSISTANT READY")
                print("🔊  Say 'computer' or 'alexa' to start")
                print("⌨️   Press Ctrl+C to stop")
                print("=" * 60)

                # Start wake word detection
                self.wake_word_detector.start_detection(self.audio_manager)

                # Start wake word audio stream
                with sd.RawInputStream(
                    samplerate=self.samplerate, 
                    blocksize=1024,
                    dtype="float32", 
                    channels=1, 
                    callback=self.audio_manager.wake_word_callback
                ):

                    while self.running:
                        try:
                            # Wait for wake word
                            await asyncio.sleep(0.1)  # Non-blocking sleep
                            
                            if self.wake_word_detector.is_wake_detected():
                                # Play beep instead of voice response
                                print("🎯 Wake word detected!")
                                self.audio_manager.play_beep()

                                # Start listening for command
                                self.listening_for_command.set()
                                
                                # Start command audio stream and listen for command
                                with sd.RawInputStream(
                                    samplerate=self.samplerate, 
                                    blocksize=8000,
                                    dtype="int16", 
                                    channels=1, 
                                    callback=self.audio_manager.command_callback
                                ):
                                    # Run command listening in thread to avoid blocking
                                    loop = asyncio.get_event_loop()
                                    command_text = await loop.run_in_executor(
                                        None, 
                                        self.speech_recognizer.recognize_command,
                                        self.audio_manager,
                                        self.listening_for_command
                                    )
                                
                                self.listening_for_command.clear()

                                # Process command asynchronously
                                await self.process_command_async(command_text)

                                print(f"\n{'=' * 30}")
                                print("🔊 Ready for next wake word...")
                                print("=" * 30)

                        except KeyboardInterrupt:
                            break

            except Exception as e:
                print(f"Main loop error: {e}")
            finally:
                self.cleanup()

        # Run the async main function
        try:
            asyncio.run(async_main())
        except KeyboardInterrupt:
            print("\n👋 Voice assistant stopped by user")

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        self.wake_word_detector.stop()
        print("\n👋 Voice assistant stopped")
