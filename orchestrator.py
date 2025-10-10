#!/usr/bin/env python3
"""
LexiQ Orchestrator - Main Query Interface
Handles user queries and returns formatted responses with case law references.
"""

from utils.query_handler import QueryHandler
import sys


def main():
    """Main orchestrator for LexiQ queries."""
    
    # Configuration
    VECTOR_STORE_DIR = "data/vector_store"
    NUM_RESULTS = 5  # Number of relevant cases to retrieve
    
    print("=" * 60)
    print("🏛️  LexiQ - Supreme Court Case Law Assistant")
    print("=" * 60)
    print()
    
    # Initialize the query handler
    query_handler = QueryHandler(
        vector_store_dir=VECTOR_STORE_DIR,
        k=NUM_RESULTS
    )
    
    try:
        query_handler.initialize()
    except Exception as e:
        print(f"❌ Error initializing query handler: {e}")
        sys.exit(1)
    
    # Interactive query loop
    print("💡 Type your legal question or 'exit' to quit.")
    print("-" * 60)
    print()
    
    while True:
        # Get user input
        user_query = input("\n📝 Your Query: ").strip()
        
        if not user_query:
            print("⚠️  Please enter a query.")
            continue
        
        if user_query.lower() in ["exit", "quit", "q"]:
            print("\n👋 Thank you for using LexiQ!")
            break
        
        # Process the query
        try:
            result = query_handler.query(user_query)
            
            print("\n" + "=" * 60)
            print("📋 RESPONSE")
            print("=" * 60)
            print()
            print(result["response"])
            print()
            print("-" * 60)
            print(f"📊 Retrieved {result['num_documents']} relevant documents")
            print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            print("Please try again.")


def query_once(question: str):
    """
    Convenience function to query once and return result.
    Useful for API integrations.
    
    Args:
        question: The legal question to ask
        
    Returns:
        Dictionary with response and metadata
    """
    VECTOR_STORE_DIR = "data/vector_store"
    NUM_RESULTS = 5
    
    query_handler = QueryHandler(
        vector_store_dir=VECTOR_STORE_DIR,
        k=NUM_RESULTS
    )
    
    query_handler.initialize()
    return query_handler.query(question)


if __name__ == "__main__":
    main()

