#!/usr/bin/env python3
"""
Command Processor Module
Handles command matching and processing using sentence embeddings
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from database_manager import DatabaseManager


class CommandProcessor:
    def __init__(self):
        # Initialize sentence transformer model
        print("Loading sentence transformer model...")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Define available commands (keeping for backward compatibility if needed)
        # self.commands = [
        #     "turn on all lights", "turn on bedroom lights", "turn off bedroom lights",
        #     "turn off living room lamp", "turn on living room lamp", "turn off all lights",
        #     "get weather", "get time", "set timer", "play music or song", "call for help", 
        #     "Bluethooth _on", "bluetooth_off", "volume_up", "volume_down"
        # ]

        
    def process_command(self, text, simple_threshold=50, intelligent_tool_threshold=30):
        """
        Process user input and find best matching tool from database.
        
        Args:
            text (str): User input text
            simple_threshold (float): Threshold for simple tool matching (0-100)
            intelligent_tool_threshold (float): Threshold for intelligent tool matching (0-100)
            
        Returns:
            tuple: (tool_type, tool_id, confidence) or (None, None, 0) if no match found
        """
        if not text.strip():
            return None, None, 0

        user_embedding = self.sentence_model.encode(text)

        # First, check simple tools
        simple_tool_embeddings = self.db_manager.get_simple_tool_embeddings()
        
        if simple_tool_embeddings:
            # Convert stored embeddings back to numpy arrays
            simple_embeddings_list = []
            simple_tool_ids = []
            
            for tool_data in simple_tool_embeddings:
                if tool_data['tool_embedding']:  # Check if embedding exists
                    # Convert bytes back to numpy array
                    embedding_array = np.frombuffer(tool_data['tool_embedding'], dtype=np.float32)
                    simple_embeddings_list.append(embedding_array)
                    simple_tool_ids.append(tool_data['tool_id'])
            
            if simple_embeddings_list:
                # Calculate similarities with simple tools
                simple_similarities = cosine_similarity([user_embedding], simple_embeddings_list)
                best_simple_index = simple_similarities.argmax()
                best_simple_confidence = simple_similarities[0, best_simple_index] * 100
                
                # Check if simple tool threshold is met
                if best_simple_confidence >= simple_threshold:
                    best_simple_tool_id = simple_tool_ids[best_simple_index]
                    return "simple", best_simple_tool_id, best_simple_confidence

        # If simple tools didn't match, check intelligent tools
        intelligent_tool_embeddings = self.db_manager.get_intelligent_tool_embeddings()
        
        if intelligent_tool_embeddings:
            # Convert stored embeddings back to numpy arrays
            intelligent_embeddings_list = []
            intelligent_tool_ids = []
            
            for tool_data in intelligent_tool_embeddings:
                if tool_data['tool_embedding']:  # Check if embedding exists
                    # Convert bytes back to numpy array
                    embedding_array = np.frombuffer(tool_data['tool_embedding'], dtype=np.float32)
                    intelligent_embeddings_list.append(embedding_array)
                    intelligent_tool_ids.append(tool_data['tool_id'])
            
            if intelligent_embeddings_list:
                # Calculate similarities with intelligent tools
                intelligent_similarities = cosine_similarity([user_embedding], intelligent_embeddings_list)
                best_intelligent_index = intelligent_similarities.argmax()
                best_intelligent_confidence = intelligent_similarities[0, best_intelligent_index] * 100
                
                # Check if intelligent tool threshold is met
                if best_intelligent_confidence >= intelligent_tool_threshold:
                    best_intelligent_tool_id = intelligent_tool_ids[best_intelligent_index]
                    return "intelligent", best_intelligent_tool_id, best_intelligent_confidence

        # No tools found that meet the thresholds
        return None, None, 0

    def get_tool_details(self, tool_type, tool_id):
        """
        Get tool details based on tool type and ID.
        
        Args:
            tool_type (str): Type of tool ("simple" or "intelligent")
            tool_id (int): ID of the tool
            
        Returns:
            dict: Tool details or None if not found
        """
        try:
            if tool_type == "simple":
                return self.db_manager.get_simple_tool(tool_id)
            elif tool_type == "intelligent":
                return self.db_manager.get_intelligent_tool(tool_id)
            else:
                return None
        except Exception as e:
            print(f"Error getting tool details: {e}")
            return None

    def generate_and_store_simple_tool_embeddings(self):
        """
        Get all simple tools from database, generate embeddings for their descriptions,
        and store them using add_simple_tool_embedding method.
        """
        try:
            print("Generating embeddings for simple tools...")
            
            # Get all simple tools as JSON
            tools_json = self.db_manager.get_all_simple_tools()
            tools_list = json.loads(tools_json)
            
            if not tools_list:
                print("No simple tools found in database")
                return False
            
            success_count = 0
            for tool in tools_list:
                tool_name = tool['tool']
                description = tool['tool_description']
                
                # Generate embedding for the description
                embedding = self.sentence_model.encode(description)
                
                # Convert numpy array to bytes for storage
                embedding_bytes = embedding.tobytes()
                
                # Store embedding in database
                if self.db_manager.add_simple_tool_embedding(tool_name, embedding_bytes):
                    print(f"Successfully stored embedding for simple tool: {tool_name}")
                    success_count += 1
                else:
                    print(f"Failed to store embedding for simple tool: {tool_name}")
            
            print(f"Successfully generated and stored embeddings for {success_count}/{len(tools_list)} simple tools")
            return success_count == len(tools_list)
            
        except Exception as e:
            print(f"Error generating simple tool embeddings: {e}")
            return False

    def generate_and_store_intelligent_tool_embeddings(self):
        """
        Get all intelligent tools from database, generate embeddings for their descriptions,
        and store them using add_intelligent_tool_embedding method.
        """
        try:
            print("Generating embeddings for intelligent tools...")
            
            # Get all intelligent tools as JSON
            tools_json = self.db_manager.get_all_intelligent_tools()
            tools_list = json.loads(tools_json)
            
            if not tools_list:
                print("No intelligent tools found in database")
                return False
            
            success_count = 0
            for tool in tools_list:
                tool_name = tool['tool']
                description = tool['tool_description']
                
                # Generate embedding for the description
                embedding = self.sentence_model.encode(description)
                
                # Convert numpy array to bytes for storage
                embedding_bytes = embedding.tobytes()
                
                # Store embedding in database
                if self.db_manager.add_intelligent_tool_embedding(tool_name, embedding_bytes):
                    print(f"Successfully stored embedding for intelligent tool: {tool_name}")
                    success_count += 1
                else:
                    print(f"Failed to store embedding for intelligent tool: {tool_name}")
            
            print(f"Successfully generated and stored embeddings for {success_count}/{len(tools_list)} intelligent tools")
            return success_count == len(tools_list)
            
        except Exception as e:
            print(f"Error generating intelligent tool embeddings: {e}")
            return False
