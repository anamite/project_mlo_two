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


class UserSettingsManager:
    def __init__(self, db_path: str = "user_settings.db"):
        """
        Initialize the UserSettingsManager with SQLite database for user data and system configurations.
        
        Args:
            db_path (str): Path to the SQLite database file for user settings
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user settings database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create User Interests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    interest TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(user_id, interest)
                )
            ''')
            
            # Create User Characteristics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_characteristics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    characteristic_name TEXT NOT NULL,
                    characteristic_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(user_id, characteristic_name)
                )
            ''')
            
            # Create System Configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    config_type TEXT DEFAULT 'string',
                    description TEXT,
                    is_editable BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    # User management methods
    def create_user(self, first_name: str, last_name: str, location: str = None) -> Optional[int]:
        """
        Create a new user.
        
        Args:
            first_name (str): User's first name
            last_name (str): User's last name
            location (str, optional): User's location
            
        Returns:
            Optional[int]: User ID if successful, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (first_name, last_name, location) VALUES (?, ?, ?)",
                    (first_name, last_name, location)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID.
        
        Args:
            user_id (int): User ID
            
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, first_name, last_name, location, created_at, updated_at FROM users WHERE id = ?",
                    (user_id,)
                )
                user = cursor.fetchone()
                
                if user:
                    return {
                        "id": user[0],
                        "first_name": user[1],
                        "last_name": user[2],
                        "location": user[3],
                        "created_at": user[4],
                        "updated_at": user[5]
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: int, first_name: str = None, last_name: str = None, location: str = None) -> bool:
        """
        Update user information.
        
        Args:
            user_id (int): User ID
            first_name (str, optional): New first name
            last_name (str, optional): New last name
            location (str, optional): New location
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            updates = []
            params = []
            
            if first_name is not None:
                updates.append("first_name = ?")
                params.append(first_name)
            if last_name is not None:
                updates.append("last_name = ?")
                params.append(last_name)
            if location is not None:
                updates.append("location = ?")
                params.append(location)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                    params
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user and all associated data.
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # User interests methods
    def add_user_interest(self, user_id: int, interest: str, priority: int = 1) -> bool:
        """
        Add an interest for a user.
        
        Args:
            user_id (int): User ID
            interest (str): Interest description
            priority (int): Interest priority (1-10, higher is more important)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO user_interests (user_id, interest, priority) VALUES (?, ?, ?)",
                    (user_id, interest, priority)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding user interest: {e}")
            return False
    
    def get_user_interests(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all interests for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            List[Dict]: List of user interests
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, interest, priority, created_at FROM user_interests WHERE user_id = ? ORDER BY priority DESC, created_at",
                    (user_id,)
                )
                interests = cursor.fetchall()
                
                return [
                    {
                        "id": interest[0],
                        "interest": interest[1],
                        "priority": interest[2],
                        "created_at": interest[3]
                    }
                    for interest in interests
                ]
        except Exception as e:
            print(f"Error getting user interests: {e}")
            return []
    
    def remove_user_interest(self, user_id: int, interest: str) -> bool:
        """
        Remove an interest from a user.
        
        Args:
            user_id (int): User ID
            interest (str): Interest to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM user_interests WHERE user_id = ? AND interest = ?",
                    (user_id, interest)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing user interest: {e}")
            return False
    
    # User characteristics methods
    def set_user_characteristic(self, user_id: int, characteristic_name: str, characteristic_value: str) -> bool:
        """
        Set a characteristic for a user.
        
        Args:
            user_id (int): User ID
            characteristic_name (str): Name of the characteristic
            characteristic_value (str): Value of the characteristic
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO user_characteristics 
                       (user_id, characteristic_name, characteristic_value, updated_at) 
                       VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                    (user_id, characteristic_name, characteristic_value)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error setting user characteristic: {e}")
            return False
    
    def get_user_characteristics(self, user_id: int) -> Dict[str, str]:
        """
        Get all characteristics for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            Dict[str, str]: Dictionary of characteristic names and values
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT characteristic_name, characteristic_value FROM user_characteristics WHERE user_id = ?",
                    (user_id,)
                )
                characteristics = cursor.fetchall()
                
                return {char[0]: char[1] for char in characteristics}
        except Exception as e:
            print(f"Error getting user characteristics: {e}")
            return {}
    
    def remove_user_characteristic(self, user_id: int, characteristic_name: str) -> bool:
        """
        Remove a characteristic from a user.
        
        Args:
            user_id (int): User ID
            characteristic_name (str): Name of the characteristic to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM user_characteristics WHERE user_id = ? AND characteristic_name = ?",
                    (user_id, characteristic_name)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing user characteristic: {e}")
            return False
    
    # System configuration methods
    def set_config(self, config_key: str, config_value: str, config_type: str = "string", 
                   description: str = None, is_editable: bool = True) -> bool:
        """
        Set a system configuration.
        
        Args:
            config_key (str): Configuration key
            config_value (str): Configuration value
            config_type (str): Type of configuration (string, integer, boolean, float, json)
            description (str, optional): Description of the configuration
            is_editable (bool): Whether the configuration can be edited
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO system_configurations 
                       (config_key, config_value, config_type, description, is_editable, updated_at) 
                       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (config_key, config_value, config_type, description, is_editable)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error setting configuration: {e}")
            return False
    
    def get_config(self, config_key: str, default_value: Any = None) -> Any:
        """
        Get a system configuration value.
        
        Args:
            config_key (str): Configuration key
            default_value (Any, optional): Default value if key not found
            
        Returns:
            Any: Configuration value with proper type conversion
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT config_value, config_type FROM system_configurations WHERE config_key = ?",
                    (config_key,)
                )
                result = cursor.fetchone()
                
                if result:
                    value, config_type = result
                    return self._convert_config_value(value, config_type)
                return default_value
        except Exception as e:
            print(f"Error getting configuration: {e}")
            return default_value
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all system configurations.
        
        Returns:
            Dict: Dictionary of all configurations with metadata
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT config_key, config_value, config_type, description, is_editable, 
                              created_at, updated_at FROM system_configurations"""
                )
                configs = cursor.fetchall()
                
                result = {}
                for config in configs:
                    key = config[0]
                    result[key] = {
                        "value": self._convert_config_value(config[1], config[2]),
                        "type": config[2],
                        "description": config[3],
                        "is_editable": bool(config[4]),
                        "created_at": config[5],
                        "updated_at": config[6]
                    }
                return result
        except Exception as e:
            print(f"Error getting all configurations: {e}")
            return {}
    
    def remove_config(self, config_key: str) -> bool:
        """
        Remove a system configuration.
        
        Args:
            config_key (str): Configuration key to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM system_configurations WHERE config_key = ?",
                    (config_key,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing configuration: {e}")
            return False
    
    def reset_config(self, config_key: str, default_value: Any) -> bool:
        """
        Reset a configuration to its default value.
        
        Args:
            config_key (str): Configuration key
            default_value (Any): Default value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        config_type = self._get_config_type(default_value)
        return self.set_config(config_key, str(default_value), config_type)
    
    def _convert_config_value(self, value: str, config_type: str) -> Any:
        """
        Convert configuration value to proper type.
        
        Args:
            value (str): String value from database
            config_type (str): Type to convert to
            
        Returns:
            Any: Converted value
        """
        try:
            if config_type == "boolean":
                return value.lower() in ("true", "1", "yes", "on")
            elif config_type == "integer":
                return int(value)
            elif config_type == "float":
                return float(value)
            elif config_type == "json":
                return json.loads(value)
            else:  # string
                return value
        except (ValueError, json.JSONDecodeError):
            return value  # Return as string if conversion fails
    
    def _get_config_type(self, value: Any) -> str:
        """
        Determine configuration type from value.
        
        Args:
            value (Any): Value to check
            
        Returns:
            str: Configuration type
        """
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, (list, dict)):
            return "json"
        else:
            return "string"
    
    # Utility methods
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users in the system.
        
        Returns:
            List[Dict]: List of all users
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, first_name, last_name, location, created_at FROM users ORDER BY created_at DESC"
                )
                users = cursor.fetchall()
                
                return [
                    {
                        "id": user[0],
                        "first_name": user[1],
                        "last_name": user[2],
                        "full_name": f"{user[1]} {user[2]}",
                        "location": user[3],
                        "created_at": user[4]
                    }
                    for user in users
                ]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get complete user profile including interests and characteristics.
        
        Args:
            user_id (int): User ID
            
        Returns:
            Optional[Dict]: Complete user profile if found, None otherwise
        """
        user = self.get_user(user_id)
        if not user:
            return None
        
        user["interests"] = self.get_user_interests(user_id)
        user["characteristics"] = self.get_user_characteristics(user_id)
        user["full_name"] = f"{user['first_name']} {user['last_name']}"
        
        return user
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the user settings database.
        
        Args:
            backup_path (str): Path for the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def initialize_default_configs(self) -> None:
        """
        Initialize default system configurations.
        This should be called once during system setup.
        """
        default_configs = {
            # Voice settings
            "wake_word": {"value": "hey assistant", "type": "string", "description": "Wake word for voice activation"},
            "voice_sensitivity": {"value": "0.5", "type": "float", "description": "Microphone sensitivity (0.0-1.0)"},
            "speech_rate": {"value": "1.0", "type": "float", "description": "Speech synthesis rate"},
            "voice_volume": {"value": "0.8", "type": "float", "description": "Voice output volume (0.0-1.0)"},
            
            # Assistant behavior
            "response_language": {"value": "en", "type": "string", "description": "Primary language for responses"},
            "assistant_personality": {"value": "helpful", "type": "string", "description": "Assistant personality type"},
            "conversation_timeout": {"value": "300", "type": "integer", "description": "Conversation timeout in seconds"},
            "max_response_length": {"value": "500", "type": "integer", "description": "Maximum response length in characters"},
            
            # System settings
            "debug_mode": {"value": "false", "type": "boolean", "description": "Enable debug logging"},
            "auto_updates": {"value": "true", "type": "boolean", "description": "Enable automatic updates"},
            "privacy_mode": {"value": "false", "type": "boolean", "description": "Enable privacy mode (local processing only)"},
            "log_conversations": {"value": "true", "type": "boolean", "description": "Log conversations for improvement"},
            
            # API settings
            "api_timeout": {"value": "30", "type": "integer", "description": "API request timeout in seconds"},
            "max_retries": {"value": "3", "type": "integer", "description": "Maximum API retry attempts"},
            
            # Device settings
            "device_name": {"value": "Voice Assistant", "type": "string", "description": "Device display name"},
            "timezone": {"value": "UTC", "type": "string", "description": "System timezone"},
            "date_format": {"value": "%Y-%m-%d", "type": "string", "description": "Date display format"},
            "time_format": {"value": "%H:%M:%S", "type": "string", "description": "Time display format"},
            
            # Performance settings
            "cache_size": {"value": "100", "type": "integer", "description": "Response cache size (MB)"},
            "cleanup_interval": {"value": "3600", "type": "integer", "description": "Database cleanup interval (seconds)"},
        }
        
        for key, config in default_configs.items():
            # Only set if doesn't exist
            if self.get_config(key) is None:
                self.set_config(
                    config_key=key,
                    config_value=config["value"],
                    config_type=config["type"],
                    description=config["description"]
                )

