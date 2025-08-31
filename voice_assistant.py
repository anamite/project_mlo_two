#!/usr/bin/env python3
"""
Voice Assistant Main Module
Orchestrates all components of the voice assistant
"""

import asyncio
import sounddevice as sd
from threading import Event

from audio_manager import AudioManager
from wake_word_detector import WakeWordDetector
from speech_recognizer import SpeechRecognizer
from command_processor import CommandProcessor
from command_executor import CommandExecutor
from message_manager import MessageManager
from user_registration import UserRegistration


class VoiceAssistant:
    def __init__(self, model_lang="en-us", samplerate=16000, voice="expr-voice-5-m"):
        self.samplerate = samplerate
        
        # Initialize all components
        print("Initializing voice assistant components...")
        self.audio_manager = AudioManager(samplerate)
        self.wake_word_detector = WakeWordDetector()
        self.speech_recognizer = SpeechRecognizer(model_lang, samplerate)
        self.command_processor = CommandProcessor()
        self.command_executor = CommandExecutor(self.audio_manager)
        self.message_manager = MessageManager()
        self.user_registration = UserRegistration(self.audio_manager)
        self.continue_conversation = False

        # Set voice
        # self.audio_manager.set_voice(voice)
        
        # State management
        self.listening_for_command = Event()
        self.running = True

        print("All models loaded successfully!")

    async def process_command_async(self, command_text):
        """Process command asynchronously and return response"""
        if command_text.strip():
            print(f"\n📥 Processing: '{command_text}'")

            self.message_manager.add_message("user", command_text)

            # Process with embedding model
            tool_type, tool_id, confidence = self.command_processor.process_command(command_text)

            print(f"🎯 Best match: '{tool_id}' ({confidence:.1f}%)")

            # Execute command and get response
            response = await self.command_executor.execute_initial_command(tool_type, tool_id, confidence, command_text)
            return response
        else:
            self.continue_conversation = False
            # beep twice
            self.audio_manager.play_low_beep()
            self.audio_manager.play_low_beep()
            return None

    def run(self):
        """Main assistant loop with async support"""
        async def async_main():
            try:
                # Check if user is registered before starting
                print("Checking user registration...")
                if not self.user_registration.ensure_user_registered():
                    print("❌ User registration required. Please complete setup before using the assistant.")
                    return
                
                print("\n" + "=" * 60)
                print("🎙️  VOICE ASSISTANT READY")
                print("🔊  Say 'computer' or 'alexa' to start")
                print("⌨️   Press Ctrl+C to stop")
                print("=" * 60)
                # speak i am ready
                self.audio_manager.auto_detect_speak("I am ready")
                # i want to also play a tone welcome.mp3
                self.audio_manager.play_sound("sources/welcome_tone.mp3")

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

                            if self.wake_word_detector.is_wake_detected() or self.continue_conversation:
                                # Play beep instead of voice response
                                print("🎯 Wake word detected!")
                                self.audio_manager.play_sound("sources/ready.mp3")  # if self.continue_conversation == True else self.audio_manager.play_beep(duration=0.5)

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

                                # Process command asynchronously and get response
                                response = await self.process_command_async(command_text)
                                
                                # Speak the response message in main loop get does not work apparently
                                if response and response["message"]:
                                    self.audio_manager.auto_detect_speak(response["message"])
                                
                                # Check if conversation should continue
                                if response and response["continue_conversation"]:
                                    print("🔄 Continuing conversation...")
                                    # Continue listening without waiting for wake word
                                    self.continue_conversation = True
                                    continue
                                else:
                                    self.continue_conversation = False
                                    
                                self.wake_word_detector.wake_detected.clear()
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
