"""
RAG System Example.

Demonstrates how to use the RAG service to add documents and query
the knowledge base with Pinecone vector store.
"""

import sys
from pathlib import Path

from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.rag_service import RAGServiceImpl


def main():
    """Run RAG system examples."""
    print("=" * 70)
    print("RAG System Example - Retrieval Augmented Generation")
    print("=" * 70)
    print()

    try:
        # Initialize LLM and RAG service
        print("1. Initializing LLM and RAG service...")
        llm = LangChainLLM()
        rag_service = RAGServiceImpl(llm=llm)
        print("✓ Services initialized successfully\n")

        # Add documents from directory
        print("2. Adding documents from data/initial_knowledge...")
        data_dir = Path("data/initial_knowledge")

        if not data_dir.exists():
            print(f"✗ Directory not found: {data_dir}")
            print("  Please create the directory and add some .txt or .md files.")
            return

        rag_service.add_documents_from_directory(
            directory=data_dir, namespace="example", recursive=True
        )
        print("✓ Documents added successfully\n")

        # Example queries
        queries = [
            "What is Agent Lab?",
            "What features does Agent Lab have?",
            "How do I use the RAG system?",
        ]

        print("3. Running example queries...\n")
        for i, query in enumerate(queries, 1):
            print(f"Query {i}: {query}")
            print("-" * 70)

            result = rag_service.query(
                query=query, top_k=3, namespace="example"
            )

            if result.success:
                print(f"Answer:\n{result.response}\n")

                if result.sources:
                    print(f"Sources ({len(result.sources)}):")
                    for source in result.sources:
                        print(
                            f"  - {source['source']} (chunk {source['chunk']})"
                        )
                else:
                    print("(No sources found)")
            else:
                print(f"✗ Error: {result.error_message}")

            print()

        # Demonstrate namespace isolation
        print("4. Demonstrating namespace isolation...\n")
        print("Adding documents to 'project-a' namespace...")
        rag_service.add_documents(
            documents=[
                "Project A uses a special authentication method with JWT tokens."
            ],
            namespace="project-a",
        )

        print("Adding documents to 'project-b' namespace...")
        rag_service.add_documents(
            documents=[
                "Project B uses OAuth2 for authentication and authorization."
            ],
            namespace="project-b",
        )

        print()
        print("Query in 'project-a' namespace:")
        result_a = rag_service.query(
            "How does authentication work?", namespace="project-a"
        )
        print(f"Answer: {result_a.response[:100]}...\n")

        print("Query in 'project-b' namespace:")
        result_b = rag_service.query(
            "How does authentication work?", namespace="project-b"
        )
        print(f"Answer: {result_b.response[:100]}...\n")

        print("=" * 70)
        print("Example completed successfully!")
        print("=" * 70)

    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - PINECONE_API_KEY")
        print("  - PINECONE_INDEX_NAME")
        print("  - PINECONE_CLOUD")
        print("  - PINECONE_REGION")
        print("\nSee .env.example for reference.")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
