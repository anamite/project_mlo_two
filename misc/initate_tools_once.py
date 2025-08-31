from database_manager import DatabaseManager
from command_processor import CommandProcessor


# Example usage and testing
if __name__ == "__main__":
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Test Simple Tools
    print("=== Testing Simple Tools ===")
    
    # Add simple tools
    db_manager.add_simple_tool("turn_off_bedroom_lamp", "turn off bedroom lamp")
    db_manager.add_simple_tool("turn_on_bedroom_lamp", "turn on bedroom lamp")
    db_manager.add_simple_tool("turn_off_living_room_lamp", "turn off living room lamp")
    db_manager.add_simple_tool("turn_on_living_room_lamp", "turn on living room lamp")
    db_manager.add_simple_tool("get_time", "get current time, what time is it?.")
    db_manager.add_simple_tool("get_weather", "get current weather")
    db_manager.add_simple_tool("turn_off_all_lights", "turn off all lights")
    db_manager.add_simple_tool("turn_on_all_lights", "turn on all lights")
    db_manager.add_simple_tool("volume_up", "turn up the volume, increase volume level")
    db_manager.add_simple_tool("volume_down", "turn down the volume, decrease volume level")
    db_manager.add_simple_tool("mute", "mute the volume")
    db_manager.add_simple_tool("unmute", "unmute the volume")
    db_manager.add_simple_tool("private_mode_on", "enable private mode, disconnect from internet")
    db_manager.add_simple_tool("private_mode_off", "disable private mode, reconnect to internet")
    db_manager.add_simple_tool("switch_voice", "switch to a different voice, change voice to male or female")


    # Get all simple tools
    print("All Simple Tools:")
    print(db_manager.get_all_simple_tools())
    
    # Test Intelligent Tools
    print("\n=== Testing Intelligent Tools ===")
    
    # Add intelligent tools
    db_manager.add_intelligent_tool(
        "Email Sender", 
        "Send emails with customizable content to people."
        "Email adresses available:(Tony Davis, td13445@gmail.com), (John Doe, john.doe@kmail.com), (Sruthi Vasudev, sruthi.vasudev@dmail.com)",
        ["recipient", "subject", "body", "attachment"]
    )
    db_manager.add_intelligent_tool(
        "calculator"
        , "Perform complex calculations and return results. Addition, subtraction, multiplication, division.",
        ["expression"]
    )
    db_manager.add_intelligent_tool(
        "Timer", 
        "Set a timer for a specified duration.",
        ["duration_min : in mins", "duration_sec : in secs"]
    )
    
    # Get all intelligent tools
    print("All Intelligent Tools:")
    print(db_manager.get_all_intelligent_tools())

    print("embedding")

    cmdp = CommandProcessor()
    
    # Generate and store embeddings for simple tools
    print("Generating simple tool embeddings...")
    simple_success = cmdp.generate_and_store_simple_tool_embeddings()
    print(f"Simple tool embeddings generated: {simple_success}")
    
    # Generate and store embeddings for intelligent tools
    print("Generating intelligent tool embeddings...")
    intelligent_success = cmdp.generate_and_store_intelligent_tool_embeddings()
    print(f"Intelligent tool embeddings generated: {intelligent_success}")
    
    # Verify embeddings were stored
    print("\nVerifying simple tool embeddings:")
    simple_embeddings = db_manager.get_simple_tool_embeddings()
    for embedding in simple_embeddings:
        has_embedding = embedding['tool_embedding'] is not None
        print(f"Tool ID {embedding['tool_id']}: {'✓' if has_embedding else '✗'} , embedding: {embedding['tool_embedding'][:10]}...")

    print("\nVerifying intelligent tool embeddings:")
    intelligent_embeddings = db_manager.get_intelligent_tool_embeddings()
    for embedding in intelligent_embeddings:
        has_embedding = embedding['tool_embedding'] is not None
        print(f"Tool ID {embedding['tool_id']}: {'✓' if has_embedding else '✗'} , embedding: {embedding['tool_embedding'][:10]}...")


    
