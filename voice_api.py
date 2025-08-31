#!/usr/bin/env python3
"""
Voice Assistant API Module
Provides HTTP-like API methods for interacting with the voice assistant system
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from database_manager import DatabaseManager, UserSettingsManager
from message_manager import MessageManager
from command_processor import CommandProcessor
from command_executor import CommandExecutor
from audio_manager import AudioManager
from api_client import APIClient


class VoiceAssistantAPI:
    """
    API class that provides GET and POST methods for the voice assistant system
    """
    
    def __init__(self):
        """Initialize the API with all necessary managers"""
        self.db_manager = DatabaseManager()
        self.message_manager = MessageManager()
        self.user_settings = UserSettingsManager()
        self.command_processor = CommandProcessor()
        self.audio_manager = AudioManager()
        self.command_executor = CommandExecutor(self.audio_manager)
        self.api_client = APIClient()
        
    # ===================
    # GET METHODS (Read-only database queries)
    # ===================
    
    def get_all_messages(self, limit: int = 100) -> Dict[str, Any]:
        """
        GET: Retrieve all messages from the conversation history
        
        Args:
            limit (int): Maximum number of messages to retrieve
            
        Returns:
            Dict containing status, message count, and messages list
        """
        try:
            messages = self.message_manager.get_last_messages(limit)
            return {
                "status": "success",
                "count": len(messages),
                "data": messages
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve messages: {str(e)}"
            }
    
    def get_user_settings(self) -> Dict[str, Any]:
        """
        GET: Retrieve current user settings
        
        Returns:
            Dict containing user settings
        """
        try:
            settings = self.user_settings.get_all_settings()
            return {
                "status": "success",
                "data": settings
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve user settings: {str(e)}"
            }
    
    def get_simple_tools(self) -> Dict[str, Any]:
        """
        GET: Retrieve all simple tools from database
        
        Returns:
            Dict containing all simple tools
        """
        try:
            tools = self.db_manager.get_all_simple_tools()
            return {
                "status": "success",
                "count": len(tools),
                "data": tools
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve simple tools: {str(e)}"
            }
    
    def get_intelligent_tools(self) -> Dict[str, Any]:
        """
        GET: Retrieve all intelligent tools from database
        
        Returns:
            Dict containing all intelligent tools
        """
        try:
            tools = self.db_manager.get_all_intelligent_tools()
            return {
                "status": "success",
                "count": len(tools),
                "data": tools
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve intelligent tools: {str(e)}"
            }
    
    def get_conversation_context(self, message_count: int = 10) -> Dict[str, Any]:
        """
        GET: Retrieve recent conversation context
        
        Args:
            message_count (int): Number of recent messages to include
            
        Returns:
            Dict containing conversation context
        """
        try:
            recent_messages = self.message_manager.get_last_messages(message_count)
            return {
                "status": "success",
                "context_size": len(recent_messages),
                "data": {
                    "recent_messages": recent_messages,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve conversation context: {str(e)}"
            }
    
    def get_tool_by_name(self, tool_name: str, tool_type: str = "simple") -> Dict[str, Any]:
        """
        GET: Retrieve a specific tool by name
        
        Args:
            tool_name (str): Name of the tool to retrieve
            tool_type (str): Type of tool ("simple" or "intelligent")
            
        Returns:
            Dict containing tool information
        """
        try:
            if tool_type == "simple":
                tool = self.db_manager.get_simple_tool_by_name(tool_name)
            else:
                tool = self.db_manager.get_intelligent_tool_by_name(tool_name)
                
            if tool:
                return {
                    "status": "success",
                    "data": tool
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Tool '{tool_name}' not found"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve tool: {str(e)}"
            }
    
    # ===================
    # POST METHODS (Write operations)
    # ===================
    
    def post_user_message(self, message: str, process_command: bool = True) -> Dict[str, Any]:
        """
        POST: Send a message to the voice assistant as if spoken by user
        
        Args:
            message (str): The message content
            process_command (bool): Whether to process the message as a command
            
        Returns:
            Dict containing response and execution results
        """
        try:
            # Add user message to conversation history
            self.message_manager.add_message("user", message)
            
            if not process_command:
                return {
                    "status": "success",
                    "message": "Message added to conversation history",
                    "user_input": message
                }
            
            # Process the command
            tool_type, tool_id, confidence = self.command_processor.process_command(message)
            
            # Execute the command (synchronous version for API)
            response = self._execute_command_sync(tool_type, tool_id, confidence, message)
            
            return {
                "status": "success",
                "user_input": message,
                "tool_matched": tool_id,
                "confidence": confidence,
                "response": response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process user message: {str(e)}"
            }
    
    def post_ai_response(self, message: str, tool_call_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        POST: Send a response from AI to the voice assistant system
        
        Args:
            message (str): The AI response message
            tool_call_info (Dict, optional): Information about any tool calls made
            
        Returns:
            Dict containing confirmation of message processing
        """
        try:
            # Add AI assistant message to conversation history
            self.message_manager.add_message("assistant", message)
            
            response_data = {
                "status": "success",
                "message": "AI response processed successfully",
                "ai_response": message,
                "timestamp": datetime.now().isoformat()
            }
            
            # If tool call information is provided, include it
            if tool_call_info:
                response_data["tool_call"] = tool_call_info
            
            return response_data
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process AI response: {str(e)}"
            }
    
    def post_system_message(self, message: str, message_type: str = "info") -> Dict[str, Any]:
        """
        POST: Send a system message to the conversation
        
        Args:
            message (str): The system message
            message_type (str): Type of system message (info, warning, error)
            
        Returns:
            Dict containing confirmation
        """
        try:
            # Format system message with type
            formatted_message = f"[{message_type.upper()}] {message}"
            
            # Add system message to conversation history
            self.message_manager.add_message("system", formatted_message)
            
            return {
                "status": "success",
                "message": "System message added successfully",
                "system_message": formatted_message,
                "message_type": message_type
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add system message: {str(e)}"
            }
    
    def post_chat_completion(self, user_message: str, use_context: bool = True) -> Dict[str, Any]:
        """
        POST: Get AI chat completion response
        
        Args:
            user_message (str): The user's message
            use_context (bool): Whether to include conversation context
            
        Returns:
            Dict containing AI response
        """
        try:
            # Add user message to history
            self.message_manager.add_message("user", user_message)
            
            # Get conversation context if requested
            context_messages = []
            if use_context:
                context_messages = self.message_manager.get_last_messages(10)
            
            # Get AI response using existing API client
            ai_response = self._get_ai_completion(user_message, context_messages)
            
            # Add AI response to history
            self.message_manager.add_message("assistant", ai_response)
            
            return {
                "status": "success",
                "user_input": user_message,
                "ai_response": ai_response,
                "used_context": use_context,
                "context_size": len(context_messages) if use_context else 0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get chat completion: {str(e)}"
            }
    
    # ===================
    # HELPER METHODS
    # ===================
    
    def _execute_command_sync(self, tool_type: str, tool_id: str, confidence: float, command_text: str) -> Dict[str, Any]:
        """
        Synchronous version of command execution for API usage
        """
        try:
            # This is a simplified synchronous version
            # In a real implementation, you might need to handle async operations differently
            
            if tool_type == "simple":
                # Execute simple tool
                result = self.command_executor.execute_simple_tool(tool_id, command_text)
            elif tool_type == "intelligent":
                # Execute intelligent tool (this might need async handling)
                result = self.command_executor.execute_intelligent_tool(tool_id, command_text)
            else:
                result = {
                    "message": "Unknown command type",
                    "continue_conversation": False
                }
                
            return result
            
        except Exception as e:
            return {
                "message": f"Error executing command: {str(e)}",
                "continue_conversation": False
            }
    
    def _get_ai_completion(self, user_message: str, context_messages: List[Dict]) -> str:
        """
        Get AI completion using the existing API client
        """
        try:
            # Build the conversation for AI
            messages = []
            
            # Add context messages
            for msg in context_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["message"]
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Use existing API client to get response
            # This is a simplified version - you might need to adapt based on your APIClient implementation
            response = self.api_client.client.chat.completions.create(
                model=self.api_client.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI response error: {str(e)}"
    
    # ===================
    # UTILITY METHODS
    # ===================
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        GET: Get overall API status and health check
        
        Returns:
            Dict containing system status
        """
        try:
            # Test database connections
            db_status = "ok"
            message_db_status = "ok"
            
            try:
                self.db_manager.get_all_simple_tools()
            except:
                db_status = "error"
                
            try:
                self.message_manager.get_last_messages(1)
            except:
                message_db_status = "error"
            
            return {
                "status": "success",
                "api_version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "tools_database": db_status,
                    "messages_database": message_db_status,
                    "audio_manager": "ok",
                    "command_processor": "ok"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"API status check failed: {str(e)}"
            }


# ===================
# EXAMPLE USAGE
# ===================

if __name__ == "__main__":
    # Initialize the API
    api = VoiceAssistantAPI()
    
    # Example GET operations
    print("=== GET EXAMPLES ===")
    
    # Get API status
    status = api.get_api_status()
    print(f"API Status: {json.dumps(status, indent=2)}")
    
    # Get recent messages
    messages = api.get_all_messages(limit=5)
    print(f"Recent Messages: {json.dumps(messages, indent=2)}")
    
    # Get simple tools
    tools = api.get_simple_tools()
    print(f"Simple Tools: {json.dumps(tools, indent=2)}")
    
    print("\n=== POST EXAMPLES ===")
    
    # Post a user message
    user_response = api.post_user_message("What time is it?")
    print(f"User Message Response: {json.dumps(user_response, indent=2)}")
    
    # Post an AI response
    ai_response = api.post_ai_response("The current time is 3:30 PM")
    print(f"AI Response: {json.dumps(ai_response, indent=2)}")
    
    # Post a system message
    system_response = api.post_system_message("System initialized successfully", "info")
    print(f"System Message: {json.dumps(system_response, indent=2)}")
