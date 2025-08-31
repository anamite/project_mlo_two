#!/usr/bin/env python3
"""
Example usage of UserSettingsManager class for user management and system configurations.
This file demonstrates how to use the new features added to database_manager.py
"""

from database_manager import UserSettingsManager

def demonstrate_user_management():
    """Demonstrate user management functionality."""
    print("=== User Management Demo ===")
    
    # Initialize the user settings manager
    user_manager = UserSettingsManager("demo_user_settings.db")
    
    # Initialize default configurations
    user_manager.initialize_default_configs()
    
    # Create a new user
    user_id = user_manager.create_user(
        first_name="John",
        last_name="Doe",
        location="New York, USA"
    )
    print(f"Created user with ID: {user_id}")
    
    # Add interests for the user
    interests = ["technology", "music", "cooking", "travel", "reading"]
    priorities = [5, 4, 3, 4, 2]
    
    for interest, priority in zip(interests, priorities):
        user_manager.add_user_interest(user_id, interest, priority)
    print(f"Added {len(interests)} interests for user")
    
    # Add characteristics for the user
    characteristics = {
        "preferred_communication_style": "casual",
        "expertise_level": "intermediate",
        "learning_preference": "visual",
        "conversation_style": "friendly",
        "response_length_preference": "medium"
    }
    
    for char_name, char_value in characteristics.items():
        user_manager.set_user_characteristic(user_id, char_name, char_value)
    print(f"Added {len(characteristics)} characteristics for user")
    
    # Get and display user profile
    profile = user_manager.get_user_profile(user_id)
    print("\n--- User Profile ---")
    print(f"Name: {profile['full_name']}")
    print(f"Location: {profile['location']}")
    print(f"Created: {profile['created_at']}")
    
    print("\nInterests:")
    for interest in profile['interests']:
        print(f"  - {interest['interest']} (Priority: {interest['priority']})")
    
    print("\nCharacteristics:")
    for char_name, char_value in profile['characteristics'].items():
        print(f"  - {char_name}: {char_value}")

def demonstrate_system_configurations():
    """Demonstrate system configuration functionality."""
    print("\n\n=== System Configuration Demo ===")
    
    user_manager = UserSettingsManager("demo_user_settings.db")
    
    # Set some custom configurations
    user_manager.set_config("custom_greeting", "Hello there!", "string", "Custom greeting message")
    user_manager.set_config("max_users", "10", "integer", "Maximum number of users")
    user_manager.set_config("enable_logging", "true", "boolean", "Enable system logging")
    user_manager.set_config("temperature_threshold", "25.5", "float", "Temperature threshold in Celsius")
    
    # Get configurations
    print("Custom configurations:")
    print(f"Greeting: {user_manager.get_config('custom_greeting')}")
    print(f"Max users: {user_manager.get_config('max_users')}")
    print(f"Logging enabled: {user_manager.get_config('enable_logging')}")
    print(f"Temperature threshold: {user_manager.get_config('temperature_threshold')}")
    
    # Get default configurations
    print("\nSome default configurations:")
    print(f"Wake word: {user_manager.get_config('wake_word')}")
    print(f"Voice volume: {user_manager.get_config('voice_volume')}")
    print(f"Debug mode: {user_manager.get_config('debug_mode')}")
    print(f"Assistant personality: {user_manager.get_config('assistant_personality')}")
    
    # Update a configuration
    user_manager.set_config("voice_volume", "0.9", "float", "Voice output volume (0.0-1.0)")
    print(f"Updated voice volume: {user_manager.get_config('voice_volume')}")
    
    # Get all configurations
    all_configs = user_manager.get_all_configs()
    print(f"\nTotal configurations: {len(all_configs)}")
    
    # Show editable configurations only
    editable_configs = {k: v for k, v in all_configs.items() if v['is_editable']}
    print(f"Editable configurations: {len(editable_configs)}")

def demonstrate_advanced_features():
    """Demonstrate advanced features."""
    print("\n\n=== Advanced Features Demo ===")
    
    user_manager = UserSettingsManager("demo_user_settings.db")
    
    # Get all users
    all_users = user_manager.get_all_users()
    print(f"Total users in system: {len(all_users)}")
    
    for user in all_users:
        print(f"  - {user['full_name']} from {user['location']} (ID: {user['id']})")
    
    # Create backup
    backup_success = user_manager.backup_database("demo_user_settings_backup.db")
    print(f"\nBackup created successfully: {backup_success}")
    
    # Update user information
    if all_users:
        first_user_id = all_users[0]['id']
        update_success = user_manager.update_user(
            first_user_id, 
            location="San Francisco, CA"
        )
        print(f"User location updated: {update_success}")
        
        # Remove an interest
        user_manager.remove_user_interest(first_user_id, "cooking")
        print("Removed 'cooking' interest from user")
        
        # Add a new characteristic
        user_manager.set_user_characteristic(first_user_id, "favorite_color", "blue")
        print("Added favorite color characteristic")

if __name__ == "__main__":
    try:
        demonstrate_user_management()
        demonstrate_system_configurations()
        demonstrate_advanced_features()
        print("\n=== Demo completed successfully! ===")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
