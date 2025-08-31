#!/usr/bin/env python3
"""
API Client Module
Handles external API calls (Groq)
"""

import os
import asyncio
from groq import Groq
import json

from message_manager import MessageManager
from database_manager import UserSettingsManager
from dotenv import load_dotenv
import os
import time
load_dotenv()  # This loads the .env file

# # Initialize
# msg_manager = MessageManager() # this manages the conversation history and to built thread context

# # Add messages
# msg_manager.add_message("user", "Hello!")
# msg_manager.add_message("assistant", "Hi there! How can I help?")

# # Get last 10 messages (efficient even with thousands of records)
# last_messages = msg_manager.get_last_messages(10)


class APIClient:
    def __init__(self, model="openai/gpt-oss-120b"):
        self.api_key = os.getenv("GROQ_API_KEY") 
        self.model = model
        self.user_settings = UserSettingsManager()
        self.client = Groq(api_key=self.api_key)
        self.response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ai_assistant_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The main response message to the user"
                        },
                        "tool_call": {
                            "type": "object",
                            "properties": {
                                "tool_name": {
                                    "type": "string",
                                    "description": "Name of the tool being called"
                                },
                                "input_variables": {
                                    "type": "object",
                                    "description": "Key-value pairs of input variables and their values",
                                    "additionalProperties": True
                                },
                                "direct_response": {
                                    "type": "boolean",
                                    "description": "Whether to get a direct response from the tool"
                                }
                            },
                            "required": ["tool_name", "input_variables", "direct_response"]
                        },
                        "continue_conversation": {
                            "type": "boolean",
                            "description": "Whether to continue the conversation (true) or end it (false)"
                        }
                    },
                    "required": ["message", "continue_conversation"],
                    "additionalProperties": False
                }
            }
        }
        self.message_manager = MessageManager()
        
        if not self.api_key:
            print("⚠️  Warning: API_KEY not found")

    async def get_ai_response(self, user_message, tool_id = None, max_tokens=8192, temperature=1, retry_count=0):
        """Make API call to Groq"""
        print(f"🤖 Asking AI: {user_message} (tool_id: {tool_id}, retry: {retry_count})")

        # Get past messages from database (already in the correct format)
        past_messages = self.message_manager.get_last_messages(10)

        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        day = time.strftime("%A", time.localtime())
        user = self.user_settings.get_all_users()
        user_name = (user[0]['first_name'] + " " + user[0]['last_name']) if user else "User"
        location = "Germany"

        if not self.api_key:
            print("❌ No API key found")
            return {"message": "Sorry, I don't have access to AI assistance right now.", "continue_conversation": False}

        # Build messages array with system prompt + past messages + current message
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Keep responses brief, friendly, and natural."
                "Keep it friendly. Add fillers for a human-like tone. Stay simple and straight to the question. "
                "Continue conversation only if it makes sense. For direct answers, stay short and kind."
                "You are voice assistant (ie; the text you give could contain expressions and details)"
                "You don't have to be overly formal, just be yourself. keep it simple.. straight answers, but casual"
                f"Additional Info:user_name: {user_name}, time: {current_time}, day: {day}, location: {location}"
                "\n\nIMPORTANT: You MUST respond in valid JSON format following the exact schema provided. Do not include any text outside the JSON structure."
                "Do not use Emojis  or icons in your text.",
            }
        ]
        
        # Add past messages (they're already in the correct format with "role" and "message" keys)
        for msg in past_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["message"]
            })

        try:
            # Run Groq call in thread pool to keep it async
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                    top_p=1,
                    reasoning_effort="medium",
                    stream=False,
                    response_format=self.response_format
                )
            )
            
            # print(f"Complete_response", completion)
            ai_response = completion.choices[0].message
            
            try:
                response_content = json.loads(ai_response.content)
                # Store the AI response in the database
                self.message_manager.add_message("assistant", response_content["message"])
                
                return response_content
                
            except (json.JSONDecodeError, KeyError) as parse_error:
                print(f"💥 Failed to parse AI response JSON: {parse_error}")
                print(f"Raw content: {ai_response.content}")
                
                # Fallback response
                fallback_message = "Sorry, I had trouble understanding that."
                self.message_manager.add_message("assistant", fallback_message)
                return {"message": fallback_message, "continue_conversation": False}
                        
        except Exception as e:
            error_str = str(e)
            print(f"💥 API call error: {e}")
            
            # Check if it's a JSON validation error and we haven't retried yet
            if ("json_validate_failed" in error_str or "Failed to generate JSON" in error_str) and retry_count == 0:
                print("🔄 JSON validation failed, retrying once...")
                # Retry with a lower temperature for more consistent output
                return await self.get_ai_response(user_message, tool_id, max_tokens, temperature=0.3, retry_count=1)
            
            error_message = "Sorry, I couldn't process your request right now."
            
            # Store the error response
            self.message_manager.add_message("assistant", error_message)

            # return json, message , continues_conversation = false
            return {"message": error_message, "continue_conversation": False}

    # async def execute_intelligent_tool_call(self, tool_name, tool_arguments):
    #     # check the tool and respond

    #     if tool_name == "calculator":
    #         result = eval(tool_arguments)
    #         response_text = str(result)
    #     else:
    #         print(f"❌ Intelligent tool not found: {tool_name}")
    #         response_text = "Sorry, I couldn't find that tool"

    #     # Speak the response
    #     if response_text:
    #         self.audio_manager.speak(response_text)
