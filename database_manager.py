import sqlite3
import json
import os
from typing import List, Dict, Any, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "tools_database.db"):
        """
        Initialize the DatabaseManager with SQLite database.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create Simple Tools table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS simple_tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    embedding_vector BLOB
                )
            ''')
            
            # Create Intelligent Tools table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS intelligent_tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT UNIQUE NOT NULL,
                    tool_description TEXT NOT NULL,
                    tool_variables TEXT NOT NULL,
                    tool_embedding_vector BLOB
                )
            ''')
            
            conn.commit()
    
    # Simple Tools methods
    def add_simple_tool(self, tool_name: str, description: str) -> bool:
        """
        Add a new simple tool to the database.
        
        Args:
            tool_name (str): Name of the tool
            description (str): Description of the tool
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO simple_tools (tool_name, description) VALUES (?, ?)",
                    (tool_name, description)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            print(f"Tool '{tool_name}' already exists in simple_tools")
            return False
        except Exception as e:
            print(f"Error adding simple tool: {e}")
            return False

    def add_simple_tool_embedding(self, tool_name: str, embedding_vector: bytes) -> bool:
        """
        Add an embedding vector for an existing simple tool.

        Args:
            tool_name (str): Name of the tool
            embedding_vector (bytes): Embedding vector for the tool

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE simple_tools SET embedding_vector = ? WHERE tool_name = ?",
                    (embedding_vector, tool_name)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding simple tool embedding: {e}")
            return False

    def get_all_simple_tools(self) -> str:
        """
        Get all simple tools as JSON string.
        
        Returns:
            str: JSON string containing all simple tools
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT tool_name, description FROM simple_tools")
                tools = cursor.fetchall()
                
                tools_list = [
                    {"tool": tool[0], "tool_description": tool[1]}
                    for tool in tools
                ]
                
                return json.dumps(tools_list, indent=2)
        except Exception as e:
            print(f"Error getting simple tools: {e}")
            return json.dumps([])
    
    def delete_simple_tool(self, tool_name: str) -> bool:
        """
        Delete a simple tool from the database.
        
        Args:
            tool_name (str): Name of the tool to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM simple_tools WHERE tool_name = ?", (tool_name,))
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    print(f"Tool '{tool_name}' not found in simple_tools")
                    return False
        except Exception as e:
            print(f"Error deleting simple tool: {e}")
            return False
    
    # Intelligent Tools methods
    def add_intelligent_tool(self, tool_name: str, tool_description: str, tool_variables: List[str]) -> bool:
        """
        Add a new intelligent tool to the database.
        
        Args:
            tool_name (str): Name of the tool
            tool_description (str): Description of the tool
            tool_variables (List[str]): List of variables for the tool
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert variables list to JSON string for storage
            variables_json = json.dumps(tool_variables)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO intelligent_tools (tool_name, tool_description, tool_variables) VALUES (?, ?, ?)",
                    (tool_name, tool_description, variables_json)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            print(f"Tool '{tool_name}' already exists in intelligent_tools")
            return False
        except Exception as e:
            print(f"Error adding intelligent tool: {e}")
            return False

    def add_intelligent_tool_embedding(self, tool_name: str, embedding_vector: bytes) -> bool:
        """
        Add an embedding vector for an existing intelligent tool.

        Args:
            tool_name (str): Name of the tool
            embedding_vector (bytes): Embedding vector for the tool

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE intelligent_tools SET tool_embedding_vector = ? WHERE tool_name = ?",
                    (embedding_vector, tool_name)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding intelligent tool embedding: {e}")
            return False

    def get_all_intelligent_tools(self) -> str:
        """
        Get all intelligent tools as JSON string.
        
        Returns:
            str: JSON string containing all intelligent tools with tool_id, tool, and tool_description
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, tool_name, tool_description, tool_variables FROM intelligent_tools")
                tools = cursor.fetchall()
                
                tools_list = [
                    {
                        "tool_id": tool[0],
                        "tool": tool[1],
                        "tool_description": tool[2],
                        "tool_variables": json.loads(tool[3])
                    }
                    for tool in tools
                ]
                
                return json.dumps(tools_list, indent=2)
        except Exception as e:
            print(f"Error getting intelligent tools: {e}")
            return json.dumps([])
    
    def delete_intelligent_tool(self, tool_name: str) -> bool:
        """
        Delete an intelligent tool from the database.
        
        Args:
            tool_name (str): Name of the tool to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM intelligent_tools WHERE tool_name = ?", (tool_name,))
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    print(f"Tool '{tool_name}' not found in intelligent_tools")
                    return False
        except Exception as e:
            print(f"Error deleting intelligent tool: {e}")
            return False
    
    # Utility methods
    def get_simple_tool_embeddings(self) -> List[Dict[str, Any]]:
        """
        Get all simple tool embeddings with their IDs.
        
        Returns:
            List[Dict]: List of dictionaries containing tool_id and tool_embedding
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, embedding_vector FROM simple_tools")
                tools = cursor.fetchall()
                
                embeddings_list = [
                    {"tool_id": tool[0], "tool_embedding": tool[1]}
                    for tool in tools
                ]
                
                return embeddings_list
        except Exception as e:
            print(f"Error getting simple tool embeddings: {e}")
            return []
    
    def get_simple_tool(self, tool_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific simple tool by ID.
        
        Args:
            tool_id (int): ID of the tool to retrieve
            
        Returns:
            Optional[Dict]: Tool data with tool_name and description if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT tool_name, description FROM simple_tools WHERE id = ?", (tool_id,))
                tool = cursor.fetchone()
                
                if tool:
                    return {"tool_name": tool[0], "description": tool[1]}
                return None
        except Exception as e:
            print(f"Error getting simple tool: {e}")
            return None

    def get_simple_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific simple tool by name.
        
        Args:
            tool_name (str): Name of the tool to retrieve
            
        Returns:
            Optional[Dict]: Tool data if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT tool_name, description FROM simple_tools WHERE tool_name = ?", (tool_name,))
                tool = cursor.fetchone()
                
                if tool:
                    return {"tool": tool[0], "tool_description": tool[1]}
                return None
        except Exception as e:
            print(f"Error getting simple tool: {e}")
            return None
    
    def get_intelligent_tool_embeddings(self) -> List[Dict[str, Any]]:
        """
        Get all intelligent tool embeddings with their IDs.
        
        Returns:
            List[Dict]: List of dictionaries containing tool_id and tool_embedding
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, tool_embedding_vector FROM intelligent_tools")
                tools = cursor.fetchall()
                
                embeddings_list = [
                    {"tool_id": tool[0], "tool_embedding": tool[1]}
                    for tool in tools
                ]
                
                return embeddings_list
        except Exception as e:
            print(f"Error getting intelligent tool embeddings: {e}")
            return []
    
    def get_intelligent_tool(self, tool_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific intelligent tool by ID.
        
        Args:
            tool_id (int): ID of the tool to retrieve
            
        Returns:
            Optional[Dict]: Tool data with tool_name and tool_description if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT tool_name, tool_description FROM intelligent_tools WHERE id = ?", (tool_id,))
                tool = cursor.fetchone()
                
                if tool:
                    return {"tool_name": tool[0], "tool_description": tool[1]}
                return None
        except Exception as e:
            print(f"Error getting intelligent tool: {e}")
            return None

    def get_intelligent_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific intelligent tool by name.
        
        Args:
            tool_name (str): Name of the tool to retrieve
            
        Returns:
            Optional[Dict]: Tool data if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, tool_name, tool_description, tool_variables FROM intelligent_tools WHERE tool_name = ?", (tool_name,))
                tool = cursor.fetchone()
                
                if tool:
                    return {
                        "tool_id": tool[0],
                        "tool": tool[1],
                        "tool_description": tool[2],
                        "tool_variables": json.loads(tool[3])
                    }
                return None
        except Exception as e:
            print(f"Error getting intelligent tool: {e}")
            return None
    

