#!/usr/bin/env python3
"""
Command Executor Module
Handles execution of recognized commands
"""

import time
from .api_client import APIClient


class CommandExecutor:
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager
        self.api_client = APIClient()

    async def execute_command(self, command, song=None, original_text=""):
        """Execute the matched command and provide voice feedback"""
        print(f"\n🚀 Executing: {command}")
        
        response_text = ""

        if command == "turn on all lights":
            print("💡 All lights are now ON")
            response_text = "All lights are now on"
            
        elif command == "turn off all lights":
            print("🔌 All lights are now OFF")
            response_text = "All lights are now off"
            
        elif "bedroom lights" in command:
            action = "ON" if "on" in command else "OFF"
            print(f"🛏️ Bedroom lights are now {action}")
            response_text = f"Bedroom lights are now {action.lower()}"
            
        elif "living room lamp" in command:
            action = "ON" if "on" in command else "OFF"
            print(f"🏠 Living room lamp is now {action}")
            response_text = f"Living room lamp is now {action.lower()}"
            
        elif command == "get weather":
            print("🌤️ Today's weather: Sunny, 22°C")
            response_text = "Today's weather is sunny, 22 degrees celsius"
            
        elif command == "get time":
            current_time = time.strftime("%H:%M")
            print(f"🕐 Current time: {current_time}")
            response_text = f"The current time is {current_time}"
            
        elif command == "set timer":
            print("⏰ Timer set for 5 minutes")
            response_text = "Timer set for 5 minutes"
            
        elif command == "play music or song":
            if song:
                print(f"🎵 Playing: {song}")
                response_text = f"Now playing {song}"
            else:
                print("🎵 Playing music...")
                response_text = "Playing music"
                
        elif command == "call for help":
            print("🚨 Emergency call initiated!")
            response_text = "Emergency call initiated"
            
        elif command == "Search for bluetooth speaker":
            print("🔍 Searching for bluetooth speaker...")
            response_text = "Searching for bluetooth speaker"
            
        elif command == "Lets ask LLM":
            print("🤖 Asking AI assistant...")
            response_text = await self.api_client.get_ai_response(original_text)
            
        else:
            print("🤖 I'll need to ask an AI assistant for that...")
            response_text = await self.api_client.get_ai_response(original_text)

        # Speak the response
        if response_text:
            self.audio_manager.speak(response_text)
