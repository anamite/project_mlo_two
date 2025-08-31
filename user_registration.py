#!/usr/bin/env python3
"""
User Registration System
Handles initial user setup and registration for the voice assistant.
"""

import sys
from typing import Optional, Dict, Any
from database_manager import UserSettingsManager
from audio_manager import AudioManager


class UserRegistration:
    def __init__(self, audio_manager: AudioManager = None, db_path: str = "user_settings.db"):
        """
        Initialize the User Registration system.
        
        Args:
            audio_manager (AudioManager, optional): Audio manager for voice interactions
            db_path (str): Path to the user settings database
        """
        self.user_manager = UserSettingsManager(db_path)
        self.audio_manager = audio_manager
        self.current_user_id = None
        
    def is_user_registered(self) -> bool:
        """
        Check if any user is registered in the system.
        
        Returns:
            bool: True if at least one user exists, False otherwise
        """
        users = self.user_manager.get_all_users()
        return len(users) > 0
    
    def get_first_registered_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the first registered user (for single-user systems).
        
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        users = self.user_manager.get_all_users()
        if users:
            return users[0]
        return None
    
    def _speak_and_print(self, message: str) -> None:
        """
        Speak a message using audio manager if available, and print to console.
        
        Args:
            message (str): Message to speak and print
        """
        print(message)
        if self.audio_manager:
            self.audio_manager.auto_detect_speak(message)
    
    def _get_user_input(self, prompt: str) -> str:
        """
        Get user input with a prompt.
        
        Args:
            prompt (str): Input prompt
            
        Returns:
            str: User input
        """
        return input(f"{prompt}: ").strip()
    
    def _confirm_input(self, prompt: str, value: str) -> bool:
        """
        Confirm user input is correct.
        
        Args:
            prompt (str): What we're confirming
            value (str): The value to confirm
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        print(f"\n{prompt}: {value}")
        confirmation = input("Is this correct? (yes/no): ").strip().lower()
        return confirmation in ['yes', 'y', 'yeah', 'yep', 'correct', 'right']
    
    def register_new_user(self) -> Optional[int]:
        """
        Register a new user through interactive prompts.
        
        Returns:
            Optional[int]: User ID if successful, None otherwise
        """
        print("\n" + "=" * 60)
        print("🎉 Welcome! Let's get you set up with your voice assistant!")
        print("=" * 60)
        
        self._speak_and_print("Hello! I'm your voice assistant. Before we can start, I need to get to know you a little better.")
        
        # Get first name
        first_name = None
        while not first_name:
            self._speak_and_print("What's your first name?")
            first_name = self._get_user_input("First name")
            
            if first_name:
                if self._confirm_input("Your first name is", first_name):
                    break
                else:
                    first_name = None
        
        # Get last name
        last_name = None
        while not last_name:
            self._speak_and_print("And what's your last name?")
            last_name = self._get_user_input("Last name")
            
            if last_name:
                if self._confirm_input("Your last name is", last_name):
                    break
                else:
                    last_name = None
        
        # Get location
        location = None
        while not location:
            self._speak_and_print("What city do you live in? You can include the state or country if you'd like.")
            location = self._get_user_input("Location (city, state/country)")
            
            if location:
                if self._confirm_input("Your location is", location):
                    break
                else:
                    location = None
        
        # Create user in database
        user_id = self.user_manager.create_user(first_name, last_name, location)
        
        if user_id:
            self.current_user_id = user_id
            self._speak_and_print(f"Great! Welcome aboard, {first_name}!")
            
            # Set up basic preferences
            self._setup_user_preferences(user_id, first_name)
            
            return user_id
        else:
            self._speak_and_print("Sorry, there was an error creating your profile. Please try again.")
            return None
    
    def _setup_user_preferences(self, user_id: int, first_name: str) -> None:
        """
        Set up basic user preferences during registration.
        
        Args:
            user_id (int): User ID
            first_name (str): User's first name
        """
        print("\n" + "=" * 50)
        print("🎨 Let's personalize your experience!")
        print("=" * 50)
        
        # Ask about preferred name/greeting
        self._speak_and_print(f"How would you like me to address you? I can call you {first_name}, or something else if you prefer.")
        preferred_name = self._get_user_input(f"Preferred name (or press Enter for '{first_name}')")
        
        if not preferred_name:
            preferred_name = first_name
        
        if self._confirm_input("I'll call you", preferred_name):
            self.user_manager.set_user_characteristic(user_id, "preferred_name", preferred_name)
        else:
            # Default to first name if they don't confirm
            self.user_manager.set_user_characteristic(user_id, "preferred_name", first_name)
        
        # Ask about greeting style
        self._speak_and_print("How would you like me to greet you? I can be formal, casual, or friendly.")
        print("Options:")
        print("1. Formal (Good morning, Good afternoon)")
        print("2. Casual (Hey, Hi there)")
        print("3. Friendly (Hello, How's it going)")
        
        greeting_style = None
        while not greeting_style:
            choice = self._get_user_input("Choose 1, 2, or 3")
            if choice == "1":
                greeting_style = "formal"
            elif choice == "2":
                greeting_style = "casual"
            elif choice == "3":
                greeting_style = "friendly"
            else:
                print("Please choose 1, 2, or 3")
        
        self.user_manager.set_user_characteristic(user_id, "greeting_style", greeting_style)
        
        # Ask about interests (optional)
        self._speak_and_print("Would you like to tell me about some of your interests? This helps me provide better assistance.")
        wants_interests = input("Add interests now? (yes/no): ").strip().lower()
        
        if wants_interests in ['yes', 'y', 'yeah', 'yep']:
            self._collect_user_interests(user_id)
        
        # Set some default characteristics
        self.user_manager.set_user_characteristic(user_id, "conversation_style", "friendly")
        self.user_manager.set_user_characteristic(user_id, "response_length_preference", "medium")
        
        print("\n" + "=" * 50)
        self._speak_and_print("Perfect! Your profile is all set up. Let's get started!")
        print("=" * 50)
    
    def _collect_user_interests(self, user_id: int) -> None:
        """
        Collect user interests during setup.
        
        Args:
            user_id (int): User ID
        """
        print("\nTell me about your interests. You can mention things like:")
        print("- Hobbies (music, cooking, gaming, reading)")
        print("- Technology interests (programming, AI, gadgets)")
        print("- Sports or activities")
        print("- Any other topics you enjoy")
        print("(Type 'done' when finished)")
        
        interests_added = 0
        while True:
            interest = self._get_user_input("Interest")
            
            if interest.lower() in ['done', 'finished', 'complete', 'stop']:
                break
            
            if interest:
                # Ask for priority level
                print("How important is this interest to you?")
                print("1 = Low, 3 = Medium, 5 = High")
                
                priority = None
                while priority is None:
                    try:
                        priority_input = self._get_user_input("Priority (1-5)")
                        priority = int(priority_input)
                        if priority < 1 or priority > 5:
                            print("Please enter a number between 1 and 5")
                            priority = None
                    except ValueError:
                        print("Please enter a valid number")
                
                # Add interest to database
                if self.user_manager.add_user_interest(user_id, interest, priority):
                    print(f"✅ Added: {interest} (Priority: {priority})")
                    interests_added += 1
                else:
                    print(f"❌ Could not add: {interest}")
        
        if interests_added > 0:
            self._speak_and_print(f"Great! I've noted your {interests_added} interests.")
        else:
            self._speak_and_print("No worries! You can always add interests later.")
    
    def ensure_user_registered(self) -> bool:
        """
        Ensure a user is registered before using the assistant.
        This should be called before starting the main assistant functionality.
        
        Returns:
            bool: True if user is registered (existing or newly created), False if registration failed
        """
        if self.is_user_registered():
            # Get the first user and set as current
            user = self.get_first_registered_user()
            if user:
                self.current_user_id = user['id']
                characteristics = self.user_manager.get_user_characteristics(user['id'])
                preferred_name = characteristics.get('preferred_name', user['first_name'])
                
                print(f"👋 Welcome back, {preferred_name}!")
                # if self.audio_manager:
                #     greeting_style = characteristics.get('greeting_style', 'friendly')
                    
                #     if greeting_style == 'formal':
                #         greeting = f"Good day, {preferred_name}. How may I assist you today?"
                #     elif greeting_style == 'casual':
                #         greeting = f"Hey {preferred_name}! What's up?"
                #     else:  # friendly
                #         greeting = f"Hello {preferred_name}! How can I help you today?"
                    
                #     self.audio_manager.auto_detect_speak(greeting)
                
                return True
            return False
        else:
            # No user registered, start registration process
            print("\n🚀 It looks like this is your first time using the voice assistant!")
            self._speak_and_print("I don't see any user profiles set up yet. Let's fix that!")
            
            user_id = self.register_new_user()
            return user_id is not None
    
    def get_current_user_id(self) -> Optional[int]:
        """
        Get the current user ID.
        
        Returns:
            Optional[int]: Current user ID if set, None otherwise
        """
        return self.current_user_id
    
    def get_current_user_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get the current user's full profile.
        
        Returns:
            Optional[Dict]: User profile if available, None otherwise
        """
        if self.current_user_id:
            return self.user_manager.get_user_profile(self.current_user_id)
        return None
    
    def get_user_characteristic(self, user_id: int, characteristic_name: str) -> Optional[str]:
        """
        Get a specific characteristic for a user.
        
        Args:
            user_id (int): User ID
            characteristic_name (str): Name of the characteristic
            
        Returns:
            Optional[str]: Characteristic value if found, None otherwise
        """
        characteristics = self.user_manager.get_user_characteristics(user_id)
        return characteristics.get(characteristic_name)


def main():
    """
    Example usage of the UserRegistration class.
    """
    print("Testing User Registration System...")
    
    # Test without audio manager
    registration = UserRegistration()
    
    if registration.ensure_user_registered():
        print("✅ User registration successful!")
        profile = registration.get_current_user_profile()
        if profile:
            print(f"Current user: {profile['full_name']}")
    else:
        print("❌ User registration failed!")


if __name__ == "__main__":
    main()
