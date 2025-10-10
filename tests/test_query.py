#!/usr/bin/env python3
"""
Test script for LexiQ query system.
Tests retrieval and response generation.
"""

from utils.query_handler import QueryHandler


def test_single_query():
    """Test a single query."""
    
    print("=" * 60)
    print("Testing LexiQ Query System")
    print("=" * 60)
    print()
    
    # Initialize query handler
    query_handler = QueryHandler(
        vector_store_dir="data/vector_store",
        k=3  # Retrieve top 3 relevant cases
    )
    
    # Load vector store
    query_handler.initialize()
    
    # Test query
    test_query = "What are the landmark cases about freedom of speech?"
    
    print(f"📝 Test Query: {test_query}")
    print()
    
    # Process query
    result = query_handler.query(test_query)
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 RESPONSE")
    print("=" * 60)
    print()
    print(result["response"])
    print()
    
    print("=" * 60)
    print("📊 METADATA")
    print("=" * 60)
    print(f"Query: {result['query']}")
    print(f"Retrieved Documents: {result['num_documents']}")
    print()
    
    print("📚 Retrieved Cases:")
    for i, doc in enumerate(result['retrieved_documents'], 1):
        print(f"\n{i}. {doc['case_title']}")
        print(f"   Citation: {doc['citation']}")
        print(f"   Page: {doc['page_number']}")
        print(f"   PDF: {doc['s3_url'] if doc['s3_url'] else 'Not available'}")


def test_multiple_queries():
    """Test multiple queries in batch."""
    
    print("\n" + "=" * 60)
    print("Testing Batch Queries")
    print("=" * 60)
    print()
    
    # Initialize query handler
    query_handler = QueryHandler(
        vector_store_dir="data/vector_store",
        k=2  # Retrieve top 2 cases per query
    )
    
    query_handler.initialize()
    
    # Test queries
    test_queries = [
        "What is the doctrine of basic structure?",
        "Cases related to Article 14 of the Constitution"
    ]
    
    # Process batch
    results = query_handler.batch_query(test_queries)
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n{'=' * 60}")
        print(f"Query {i}: {result['query']}")
        print("=" * 60)
        print(result['response'])
        print()


if __name__ == "__main__":
    # Run single query test
    test_single_query()
    
    # Uncomment to test batch queries
    # test_multiple_queries()

