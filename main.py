#!/usr/bin/env python3
"""
Main script for the Voice Assistant
Handles command line arguments and starts the assistant
"""

import argparse
import sounddevice as sd
from voice_assistant import VoiceAssistant


def main():
    """Main entry point for the voice assistant"""
    parser = argparse.ArgumentParser(
        description="Voice Assistant with Wake Word Detection, TTS, and OpenRouter API"
    )
    parser.add_argument(
        "-m", "--model", 
        type=str, 
        default="en-us",
        help="VOSK language model (default: en-us)"
    )
    parser.add_argument(
        "-r", "--samplerate", 
        type=int, 
        default=16000,
        help="Sample rate (default: 16000)"
    )
    parser.add_argument(
        "-l", "--list-devices", 
        action="store_true",
        help="List audio devices and exit"
    )
    parser.add_argument(
        "-v", "--voice", 
        type=str, 
        default="expr-voice-2-m",
        help="TTS voice (default: expr-voice-2-m)"
    )

    args = parser.parse_args()

    if args.list_devices:
        print("Available audio devices:")
        print(sd.query_devices())
        return

    # Create and run assistant
    try:
        assistant = VoiceAssistant(
            model_lang=args.model, 
            samplerate=args.samplerate,
            voice=args.voice
        )
        assistant.run()
    except Exception as e:
        print(f"Failed to start voice assistant: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
