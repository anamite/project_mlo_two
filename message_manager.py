import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class MessageManager:
    def __init__(self, db_path: str = "messages.db"):
        """
        Initialize the MessageManager with SQLite database.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            ''')
            
            # Create index on timestamp for efficient ORDER BY queries
            # This is crucial for fast retrieval of last N messages
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)
            ''')
            
            conn.commit()
    
    def add_message(self, role: str, message: str) -> bool:
        """
        Add a new message to the database.
        
        Args:
            role (str): Role of the message sender (e.g., 'user', 'assistant', 'system')
            message (str): The message content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (timestamp, role, message) VALUES (?, ?, ?)",
                    (timestamp, role, message)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def get_last_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the last N messages efficiently using timestamp index.
        This method is optimized to be fast even with thousands of messages.
        
        Args:
            limit (int): Number of messages to retrieve (default: 10)
            
        Returns:
            List[Dict]: List of message dictionaries in chronological order (oldest first)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Use ORDER BY timestamp DESC with LIMIT for efficiency
                # The timestamp index makes this very fast
                cursor.execute('''
                    SELECT id, timestamp, role, message 
                    FROM messages 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                messages = cursor.fetchall()
                
                # Convert to list of dictionaries and reverse to get chronological order
                messages_list = []
                for msg in reversed(messages):  # Reverse to get oldest first
                    messages_list.append({
                        # "id": msg[0],
                        # "timestamp": msg[1],
                        # "datetime": datetime.fromtimestamp(msg[1]).isoformat(),
                        "role": msg[2],
                        "message": msg[3]
                    })
                
                return messages_list
                
        except Exception as e:
            print(f"Error getting last messages: {e}")
            return []
    
    def get_messages_count(self) -> int:
        """
        Get total count of messages in the database.
        
        Returns:
            int: Total number of messages
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM messages")
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error getting messages count: {e}")
            return 0
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific message by ID.
        
        Args:
            message_id (int): ID of the message to retrieve
            
        Returns:
            Optional[Dict]: Message data if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, timestamp, role, message FROM messages WHERE id = ?", 
                    (message_id,)
                )
                msg = cursor.fetchone()
                
                if msg:
                    return {
                        "id": msg[0],
                        "timestamp": msg[1],
                        "datetime": datetime.fromtimestamp(msg[1]).isoformat(),
                        "role": msg[2],
                        "message": msg[3]
                    }
                return None
        except Exception as e:
            print(f"Error getting message by ID: {e}")
            return None
    
    def delete_message(self, message_id: int) -> bool:
        """
        Delete a message from the database.
        
        Args:
            message_id (int): ID of the message to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    print(f"Message with ID '{message_id}' not found")
                    return False
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False
    
    def clear_all_messages(self) -> bool:
        """
        Clear all messages from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages")
                conn.commit()
                return True
        except Exception as e:
            print(f"Error clearing messages: {e}")
            return False
    
    def get_messages_by_role(self, role: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get messages filtered by role.
        
        Args:
            role (str): Role to filter by
            limit (int): Optional limit on number of messages to return
            
        Returns:
            List[Dict]: List of message dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if limit:
                    cursor.execute('''
                        SELECT id, timestamp, role, message 
                        FROM messages 
                        WHERE role = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (role, limit))
                else:
                    cursor.execute('''
                        SELECT id, timestamp, role, message 
                        FROM messages 
                        WHERE role = ? 
                        ORDER BY timestamp DESC
                    ''', (role,))
                
                messages = cursor.fetchall()
                
                messages_list = []
                for msg in reversed(messages):  # Reverse to get chronological order
                    messages_list.append({
                        "id": msg[0],
                        "timestamp": msg[1],
                        "datetime": datetime.fromtimestamp(msg[1]).isoformat(),
                        "role": msg[2],
                        "message": msg[3]
                    })
                
                return messages_list
                
        except Exception as e:
            print(f"Error getting messages by role: {e}")
            return []


# Example usage:
if __name__ == "__main__":
    # Initialize message manager
    msg_manager = MessageManager()
    
    # Add some test messages
    msg_manager.add_message("user", "Hello, how are you?")
    msg_manager.add_message("assistant", "I'm doing well, thank you! How can I help you today?")
    msg_manager.add_message("user", "Can you help me with Python programming?")
    msg_manager.add_message("assistant", "Of course! I'd be happy to help you with Python programming.")
    
    # Get last 10 messages (or all if less than 10)
    last_messages = msg_manager.get_last_messages(10)
    print("Last messages:")
    for msg in last_messages:
        print(f"[{msg['datetime']}] {msg['role']}: {msg['message']}")
    
    # Get message count
    count = msg_manager.get_messages_count()
    print(f"\nTotal messages: {count}")
