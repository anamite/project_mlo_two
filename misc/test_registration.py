#!/usr/bin/env python3
"""
Test script for User Registration System
This demonstrates the registration flow without the full voice assistant.
"""

from user_registration import UserRegistration

def main():
    print("=" * 60)
    print("🧪 USER REGISTRATION SYSTEM TEST")
    print("=" * 60)
    
    # Create registration system (without audio manager for testing)
    registration = UserRegistration(audio_manager=None, db_path="test_user_settings.db")
    
    # Check and handle user registration
    if registration.ensure_user_registered():
        print("\n✅ Registration process completed successfully!")
        
        # Display user profile
        profile = registration.get_current_user_profile()
        if profile:
            print("\n📋 User Profile Summary:")
            print(f"   Name: {profile['full_name']}")
            print(f"   Location: {profile['location']}")
            print(f"   Created: {profile['created_at']}")
            
            if profile['interests']:
                print(f"   Interests: {len(profile['interests'])} registered")
                for interest in profile['interests'][:3]:  # Show first 3
                    print(f"     - {interest['interest']} (Priority: {interest['priority']})")
                if len(profile['interests']) > 3:
                    print(f"     ... and {len(profile['interests']) - 3} more")
            
            if profile['characteristics']:
                print(f"   Preferences: {len(profile['characteristics'])} set")
                for key, value in list(profile['characteristics'].items())[:3]:  # Show first 3
                    print(f"     - {key}: {value}")
                if len(profile['characteristics']) > 3:
                    print(f"     ... and {len(profile['characteristics']) - 3} more")
        
        print("\n🚀 Ready to start voice assistant!")
    else:
        print("\n❌ Registration process failed or was cancelled.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
