"""
Example: User Profile Extraction Demo

Demonstrates how to use the profile memory system to extract
and persist user information from conversations.
"""

import json
import os
from datetime import datetime

from agentlab.agents.memory_processor import LongTermMemoryProcessor
from agentlab.config.memory_config import MemoryConfig
from agentlab.database.crud import (
    create_chat_message,
    get_user_profile,
    delete_user_profile,
    initialize_database,
)
from agentlab.models import ChatMessage


def setup_example_conversation(session_id: str):
    """Create example conversation with user information."""
    
    messages = [
        ("user", "Hi! My name is Maria and I'm 28 years old."),
        ("assistant", "Nice to meet you Maria! How can I help you today?"),
        ("user", "I'm a data scientist working at a tech company in Barcelona."),
        ("assistant", "That's great! Data science is such an exciting field."),
        ("user", "Yes! I specialize in machine learning and natural language processing."),
        ("assistant", "Those are really powerful areas. What kind of projects do you work on?"),
        ("user", "I'm building chatbots and recommendation systems. I love Python and PyTorch."),
        ("assistant", "Excellent tools! PyTorch is great for deep learning."),
        ("user", "I'm also learning about LangChain and vector databases. My goal is to become an AI engineer."),
        ("assistant", "That's a wonderful goal! You're already on the right path."),
    ]
    
    print(f"\n{'='*60}")
    print("Creating example conversation...")
    print(f"{'='*60}\n")
    
    for role, content in messages:
        create_chat_message(
            session_id=session_id,
            role=role,
            content=content,
        )
        print(f"{role.upper()}: {content}")
    
    print(f"\n✓ Created {len(messages)} messages\n")


def extract_profile_example(session_id: str):
    """Extract profile from conversation."""
    
    print(f"{'='*60}")
    print("Extracting user profile with LLM...")
    print(f"{'='*60}\n")
    
    # Initialize processor
    config = MemoryConfig.from_env()
    processor = LongTermMemoryProcessor(config=config)
    
    # Extract and store profile
    profile = processor.extract_and_store_profile(
        session_id=session_id,
        incremental=False,
    )
    
    print("📊 Extracted Profile:")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    print()
    
    return profile


def retrieve_profile_example():
    """Retrieve stored profile."""
    
    print(f"{'='*60}")
    print("Retrieving stored profile from database...")
    print(f"{'='*60}\n")
    
    profile_row = get_user_profile()
    
    if profile_row:
        print("✓ Profile found in database:")
        print(f"  Version: {profile_row['version']}")
        print(f"  Last Updated: {profile_row['updated_at']}")
        print(f"  Created: {profile_row['created_at']}")
        print(f"\n📋 Profile Data:")
        print(json.dumps(profile_row['profile_data'], indent=2, ensure_ascii=False))
    else:
        print("❌ No profile found in database")
    
    print()
    return profile_row


def update_profile_example(session_id: str):
    """Update profile with new conversation."""
    
    print(f"\n{'='*60}")
    print("Adding new conversation...")
    print(f"{'='*60}\n")
    
    new_messages = [
        ("user", "By the way, I forgot to mention - I also speak Spanish and English fluently."),
        ("assistant", "That's impressive! Being bilingual is a great asset."),
        ("user", "Thanks! I prefer detailed explanations with code examples when learning new topics."),
        ("assistant", "Noted! I'll make sure to provide comprehensive examples."),
    ]
    
    for role, content in new_messages:
        create_chat_message(
            session_id=session_id,
            role=role,
            content=content,
        )
        print(f"{role.upper()}: {content}")
    
    print(f"\n✓ Added {len(new_messages)} new messages\n")
    
    # Re-extract profile (incremental mode)
    print(f"{'='*60}")
    print("Updating profile with new information...")
    print(f"{'='*60}\n")
    
    config = MemoryConfig.from_env()
    processor = LongTermMemoryProcessor(config=config)
    
    updated_profile = processor.extract_and_store_profile(
        session_id=session_id,
        incremental=True,  # Only process new messages
    )
    
    print("📊 Updated Profile:")
    print(json.dumps(updated_profile, indent=2, ensure_ascii=False))
    print()
    
    return updated_profile


def cleanup_example():
    """Clean up example data."""
    
    print(f"{'='*60}")
    print("Cleaning up example data...")
    print(f"{'='*60}\n")
    
    deleted = delete_user_profile()
    
    if deleted:
        print("✓ Profile deleted")
    else:
        print("❌ No profile to delete")
    
    print()


def main():
    """Run the complete example."""
    
    print("\n" + "="*60)
    print(" USER PROFILE EXTRACTION DEMO")
    print("="*60 + "\n")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not set in environment")
        print("   Please set it to run this example:")
        print("   export OPENAI_API_KEY='your-api-key'")
        return
    
    session_id = f"demo-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    try:
        # Ensure database is initialized
        initialize_database()
        
        # Step 1: Create example conversation
        setup_example_conversation(session_id)
        
        # Step 2: Extract profile
        extract_profile_example(session_id)
        
        # Step 3: Retrieve stored profile
        retrieve_profile_example()
        
        # Step 4: Update with new information
        update_profile_example(session_id)
        
        # Step 5: Retrieve updated profile
        final_profile = retrieve_profile_example()
        
        # Show what changed
        if final_profile:
            print(f"{'='*60}")
            print("Summary")
            print(f"{'='*60}\n")
            print(f"✓ Profile successfully extracted and stored")
            print(f"✓ Version: {final_profile['version']}")
            print(f"✓ Attributes extracted: {len(final_profile['profile_data'])}")
            print(f"\n🎯 Key Information Captured:")
            
            data = final_profile['profile_data']
            if 'user_name' in data:
                print(f"   • Name: {data['user_name']}")
            if 'age' in data:
                print(f"   • Age: {data['age']}")
            if 'occupation' in data:
                print(f"   • Occupation: {data['occupation']}")
            if 'home' in data:
                print(f"   • Location: {data['home']}")
            if 'expertise_areas' in data:
                print(f"   • Expertise: {', '.join(data['expertise_areas'])}")
            if 'interests' in data:
                print(f"   • Interests: {', '.join(data['interests'])}")
            if 'goals' in data:
                print(f"   • Goals: {', '.join(data['goals'])}")
            
            # Show any custom fields added by LLM
            known_fields = {
                'user_name', 'age', 'occupation', 'home', 'expertise_areas',
                'interests', 'goals', 'conversation_preferences', 'technical_context',
                'learning_style'
            }
            custom_fields = set(data.keys()) - known_fields
            if custom_fields:
                print(f"\n📝 Custom Fields Added by LLM:")
                for field in custom_fields:
                    print(f"   • {field}: {data[field]}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Optional: Cleanup
        response = input("\n\nDelete the example profile? (y/N): ")
        if response.lower() == 'y':
            cleanup_example()
    
    print("\n" + "="*60)
    print(" Demo Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
