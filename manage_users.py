#!/usr/bin/env python3
"""
Standalone User Registration Script
Run this script to register a new user or manage existing users.
"""

import sys
from user_registration import UserRegistration
from database_manager import UserSettingsManager

def list_existing_users():
    """List all existing users."""
    user_manager = UserSettingsManager()
    users = user_manager.get_all_users()
    
    if not users:
        print("No users found in the system.")
        return
    
    print(f"\nFound {len(users)} user(s):")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['full_name']} from {user['location']} (ID: {user['id']})")
        print(f"   Created: {user['created_at']}")

def register_new_user():
    """Register a new user."""
    print("\n🚀 Starting new user registration...")
    registration = UserRegistration()
    user_id = registration.register_new_user()
    
    if user_id:
        print(f"\n✅ User registered successfully with ID: {user_id}")
        return True
    else:
        print("\n❌ Registration failed.")
        return False

def reset_all_users():
    """Reset all users (for testing purposes)."""
    confirm = input("\n⚠️  This will delete ALL users and their data. Are you sure? (type 'DELETE ALL'): ")
    if confirm != "DELETE ALL":
        print("Operation cancelled.")
        return
    
    user_manager = UserSettingsManager()
    users = user_manager.get_all_users()
    
    deleted = 0
    for user in users:
        if user_manager.delete_user(user['id']):
            deleted += 1
    
    print(f"🗑️  Deleted {deleted} user(s).")

def main():
    """Main menu for user management."""
    while True:
        print("\n" + "=" * 50)
        print("👤 USER REGISTRATION MANAGER")
        print("=" * 50)
        print("1. List existing users")
        print("2. Register new user")
        print("3. Reset all users (DELETE ALL)")
        print("4. Test registration system")
        print("5. Exit")
        print("=" * 50)
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            list_existing_users()
        elif choice == "2":
            register_new_user()
        elif choice == "3":
            reset_all_users()
        elif choice == "4":
            # Test the full registration flow
            registration = UserRegistration()
            if registration.ensure_user_registered():
                print("✅ Registration test completed!")
            else:
                print("❌ Registration test failed!")
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please choose 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 User registration manager stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
