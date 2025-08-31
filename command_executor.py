#!/usr/bin/env python3
"""
Command Executor Module
Handles execution of recognized commands
"""

import time
from api_client import APIClient
from database_manager import DatabaseManager


class CommandExecutor:
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager
        self.api_client = APIClient()
        self.db_manager = DatabaseManager()

    async def execute_initial_command(self, tool_type, tool_id, confidence, command_text):
        """
        Execute the matched command based on tool type and ID
        
        Args:
            tool_type (str): Type of tool ("simple" or "intelligent")
            tool_id (int): ID of the tool in database
            confidence (float): Confidence score of the match
            command_text (str): Original user command text
        """
        print(f"\n🚀 Executing {tool_type} tool (ID: {tool_id}) with confidence: {confidence:.2f}%")
        
        response = ""

        if tool_type == "simple":
            # Get simple tool details from database
            tool_details = self.db_manager.get_simple_tool(tool_id)
            
            if tool_details:
                tool_name = tool_details['tool_name']
                tool_description = tool_details['description']
                
                print(f"📋 Simple Tool: {tool_name}")
                print(f"📝 Description: {tool_description}")
                
                # Process simple tool based on tool name
                if tool_name == "turn_on_bedroom_lamp":
                    response = {"message": "Bedroom lamp is now on", "continue_conversation": False}
                elif tool_name == "turn_off_bedroom_lamp":
                    response = {"message": "Bedroom lamp is now off", "continue_conversation": False}   

                elif tool_name == "turn_on_living_room_lamp":
                    response = {"message": "Living room lamp is now on", "continue_conversation": False}

                elif tool_name == "turn_off_living_room_lamp":
                    response = {"message": "Living room lamp is now off", "continue_conversation": False}

                elif tool_name == "turn_on_all_lights":
                    response = {"message": "All lights are now on", "continue_conversation": False}

                elif tool_name == "turn_off_all_lights":
                    response = {"message": "All lights are now off", "continue_conversation": False}

                elif tool_name == "get_time":
                    response = {"message": f"The current time is {time.strftime('%I:%M %p', time.localtime())}", "continue_conversation": False}

                elif tool_name == "get_weather":
                    response = {"message": "The current weather is sunny", "continue_conversation": False}

                elif tool_name == "volume_up":
                    response = {"message": "Volume is now up", "continue_conversation": False}

                elif tool_name == "volume_down":
                    response = {"message": "Volume is now down", "continue_conversation": False}

                elif tool_name == "mute":
                    response = {"message": "Volume is now muted", "continue_conversation": False}

                elif tool_name == "unmute":
                    response = {"message": "Volume is now unmuted", "continue_conversation": False}
                elif tool_name == "private_mode_on":
                    response = {"message": "Private mode is now enabled", "continue_conversation": False}
                elif tool_name == "private_mode_off":
                    response = {"message": "Private mode is now disabled", "continue_conversation": False}
                elif tool_name == "switch_voice":
                    response = {"message": "Voice has been switched", "continue_conversation": False}

                else:
                    # Unknown simple tool - provide generic response
                    print(f"⚙️ Executing simple tool: {tool_name}")
                    response = {"message": f"Executing {tool_name}", "continue_conversation": False}
            else:
                print("❌ Simple tool not found in database")
                response = {"message": "Sorry, I couldn't find that tool", "continue_conversation": False}      

        elif tool_type == "intelligent":
            # For intelligent tools, pass to LLM with tool ID
            print(f"🤖 Calling AI assistant with intelligent tool ID: {tool_id}")
            
            # Call LLM with tool context
            response = await self.api_client.get_ai_response(user_message=command_text, tool_id=tool_id)
            
        else:
            # No tool found - fallback to LLM
            print("🤖 No specific tool found, asking AI assistant...")
            response = await self.api_client.get_ai_response(command_text, tool_id=None)

        # Debug the response
        print(f"🔍 Response received: '{response}' (type: {type(response)})")
        

        return response
        # # Speak the response
        # if response:
        #     print(f"🔊 About to speak: {response}")
            
        # else:
        #     print("❌ No response to speak - response is empty or None")


