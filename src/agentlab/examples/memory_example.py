#!/usr/bin/env python3
"""
Memory module example.

Demonstrates short-term and long-term memory capabilities including
semantic search, profile building, and episodic summarization.
"""

import os
from datetime import datetime

from dotenv import load_dotenv

from agentlab.core.memory_service import IntegratedMemoryService
from agentlab.models import ChatMessage

# Load environment variables
load_dotenv()


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    """Run memory module examples."""
    print("🧠 Agent Lab Memory Module Example")
    print("=" * 60)

    # Verify configuration
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("\n❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set these in your .env file.")
        return

    print("\n✅ Configuration loaded")
    print(f"   Database: {os.getenv('DB_NAME')}@{os.getenv('DB_HOST')}")
    print(f"   Memory Type: {os.getenv('MEMORY_TYPE', 'buffer')}")
    print(f"   Long-term: {os.getenv('ENABLE_LONG_TERM', 'true')}")
    print(f"   Storage: {os.getenv('SEMANTIC_STORAGE', 'hybrid')}")

    # Initialize memory service
    try:
        memory_service = IntegratedMemoryService()
        print("✅ Memory service initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize memory service: {e}")
        print(
            "\nMake sure your database is running and environment is configured."
        )
        return

    # Use a unique session ID for this example
    session_id = f"example-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Example 1: Adding messages to memory
    print_section("Example 1: Adding Messages to Memory")

    messages = [
        ("user", "Hello! I'm learning Python and interested in data science."),
        (
            "assistant",
            "That's great! Python is excellent for data science. "
            "What aspect are you most interested in?",
        ),
        (
            "user",
            "I want to learn about machine learning and data visualization.",
        ),
        (
            "assistant",
            "Perfect! I recommend starting with pandas for data manipulation, "
            "matplotlib/seaborn for visualization, and scikit-learn for ML.",
        ),
        ("user", "Can you help me with a specific pandas question?"),
        (
            "assistant",
            "Of course! What would you like to know about pandas?",
        ),
    ]

    print(f"Adding {len(messages)} messages to session: {session_id}\n")

    for role, content in messages:
        message = ChatMessage(
            role=role, content=content, timestamp=datetime.now()
        )
        memory_service.add_message(session_id, message)
        print(f"✅ {role}: {content[:50]}...")

    # Example 2: Retrieving conversation history
    print_section("Example 2: Retrieving Conversation History")

    history = memory_service.get_messages(session_id, limit=10)
    print(f"Retrieved {len(history)} messages:\n")

    for i, msg in enumerate(history, 1):
        print(f"{i}. [{msg.role}] {msg.content}")

    # Example 3: Getting enriched memory context
    print_section("Example 3: Enriched Memory Context")

    try:
        context = memory_service.get_context(session_id, max_tokens=2000)

        print("Short-term Context:")
        print(f"  {context.short_term_context[:200]}...\n")

        if context.semantic_facts:
            print("Semantic Facts:")
            for fact in context.semantic_facts:
                print(f"  • {fact}")
        else:
            print("Semantic Facts: (Long-term memory not configured)")

        print(f"\nUser Profile:")
        if context.user_profile:
            for key, value in context.user_profile.items():
                if key == "top_topics" and isinstance(value, list):
                    print(f"  {key}:")
                    for topic in value[:5]:
                        if isinstance(topic, dict):
                            print(
                                f"    - {topic.get('word')}: "
                                f"{topic.get('count')}"
                            )
                else:
                    print(f"  {key}: {value}")
        else:
            print("  (No profile data yet)")

        if context.episodic_summary:
            print(f"\nEpisodic Summary:")
            print(f"  {context.episodic_summary}")

        if context.procedural_patterns:
            print(f"\nProcedural Patterns:")
            for pattern in context.procedural_patterns:
                print(f"  • {pattern}")

    except Exception as e:
        print(f"⚠️  Could not retrieve full context: {e}")
        print(
            "   (This is normal if Pinecone or OpenAI keys are not configured)"
        )

    # Example 4: Memory statistics
    print_section("Example 4: Memory Statistics")

    try:
        stats = memory_service.get_stats(session_id)

        print(f"Session: {stats.session_id}")
        print(f"Total Messages: {stats.message_count}")
        print(f"Token Count: {stats.token_count}")
        print(f"Semantic Facts: {stats.semantic_facts_count}")
        print(f"Profile Attributes: {stats.profile_attributes_count}")

        if stats.oldest_message_date:
            print(
                f"Oldest Message: "
                f"{stats.oldest_message_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        if stats.newest_message_date:
            print(
                f"Newest Message: "
                f"{stats.newest_message_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )

    except Exception as e:
        print(f"⚠️  Could not retrieve stats: {e}")

    # Example 5: Semantic search (if configured)
    print_section("Example 5: Semantic Search")

    if os.getenv("SEMANTIC_STORAGE") in ("pinecone", "hybrid") and os.getenv(
        "PINECONE_API_KEY"
    ):
        try:
            print("Searching for 'machine learning'...\n")
            results = memory_service.search_semantic(
                query="machine learning", session_id=session_id, top_k=3
            )

            if results:
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. Score: {result['score']:.3f}")
                    print(f"   Text: {result['text'][:100]}...")
                    print(f"   Session: {result['session_id']}")
            else:
                print("No results found (embeddings may not be stored yet)")

        except Exception as e:
            print(f"⚠️  Semantic search failed: {e}")
    else:
        print("⚠️  Semantic search not configured")
        print(
            "   Set SEMANTIC_STORAGE=hybrid and PINECONE_API_KEY to enable"
        )

    # Example 6: Clean up
    print_section("Example 6: Cleanup")

    response = input(f"\nClear session memory for {session_id}? (y/N): ")

    if response.lower() == "y":
        try:
            memory_service.clear_session(session_id)
            print(f"✅ Cleared memory for session {session_id}")
        except Exception as e:
            print(f"❌ Failed to clear memory: {e}")
    else:
        print(f"ℹ️  Session preserved. Session ID: {session_id}")
        print(
            "   You can query this session later using the API or Python code."
        )

    print("\n" + "=" * 60)
    print("Example completed! 🎉")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
