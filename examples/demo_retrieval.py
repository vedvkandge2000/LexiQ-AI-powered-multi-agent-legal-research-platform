#!/usr/bin/env python3
"""
Demo script for LexiQ Retrieval System.
Demonstrates all key features with example queries.
"""

from utils.query_handler import QueryHandler
from utils.retriever import LegalDocumentRetriever
import time


def print_separator(char="=", length=70):
    """Print a separator line."""
    print(char * length)


def demo_basic_query():
    """Demonstrate basic query functionality."""
    print_separator()
    print("DEMO 1: Basic Query")
    print_separator()
    print()
    
    # Initialize
    handler = QueryHandler(vector_store_dir="data/vector_store", k=3)
    handler.initialize()
    
    # Query
    query = "What are the key principles of freedom of speech under the Constitution?"
    print(f"📝 Query: {query}")
    print()
    
    start = time.time()
    result = handler.query(query)
    elapsed = time.time() - start
    
    # Display response
    print_separator("-")
    print("RESPONSE:")
    print_separator("-")
    print(result["response"])
    print()
    print_separator("-")
    print(f"⏱️  Query processed in {elapsed:.2f} seconds")
    print(f"📊 Retrieved {result['num_documents']} relevant documents")
    print_separator("-")
    print()


def demo_retrieval_with_metadata():
    """Demonstrate retrieval with metadata access."""
    print_separator()
    print("DEMO 2: Retrieval with Metadata")
    print_separator()
    print()
    
    # Initialize
    handler = QueryHandler(vector_store_dir="data/vector_store", k=5)
    handler.initialize()
    
    # Query
    query = "Cases related to Article 14 equality"
    print(f"📝 Query: {query}")
    print()
    
    result = handler.query(query)
    
    # Display sources with metadata
    print("📚 RETRIEVED SOURCES:")
    print()
    
    for i, doc in enumerate(result['retrieved_documents'], 1):
        print(f"{i}. {doc['case_title']}")
        print(f"   📖 Citation: {doc['citation']}")
        print(f"   📄 Page: {doc['page_number']}")
        print(f"   🔗 PDF: {doc['s3_url'] if doc['s3_url'] else 'Not available'}")
        print(f"   📝 Preview: {doc['content_preview'][:150]}...")
        print()
    
    print_separator("-")
    print()


def demo_search_only():
    """Demonstrate pure search without Claude."""
    print_separator()
    print("DEMO 3: Pure Search (No Claude)")
    print_separator()
    print()
    
    # Initialize retriever directly
    retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
    retriever.load_vector_store()
    
    # Search
    query = "judicial review"
    print(f"🔍 Searching for: {query}")
    print()
    
    # Retrieve with scores
    results = retriever.retrieve_with_scores(query, k=5)
    
    print("SEARCH RESULTS (with relevance scores):")
    print()
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. [{score:.4f}] {doc.metadata.get('case_title', 'Unknown')}")
        print(f"   {doc.metadata.get('citation', 'No citation')} - Page {doc.metadata.get('page_number', 'N/A')}")
        print()
    
    print_separator("-")
    print()


def demo_batch_queries():
    """Demonstrate batch query processing."""
    print_separator()
    print("DEMO 4: Batch Query Processing")
    print_separator()
    print()
    
    # Initialize
    handler = QueryHandler(vector_store_dir="data/vector_store", k=2)
    handler.initialize()
    
    # Multiple queries
    queries = [
        "What is the doctrine of basic structure?",
        "Explain judicial activism in India"
    ]
    
    print(f"Processing {len(queries)} queries in batch...")
    print()
    
    start = time.time()
    results = handler.batch_query(queries)
    elapsed = time.time() - start
    
    # Display results
    for i, result in enumerate(results, 1):
        print_separator("-")
        print(f"QUERY {i}: {result['query']}")
        print_separator("-")
        print(result['response'][:500] + "...")  # First 500 chars
        print()
        print(f"📊 Sources: {result['num_documents']} documents")
        print()
    
    print_separator("-")
    print(f"⏱️  {len(queries)} queries processed in {elapsed:.2f} seconds")
    print(f"⚡ Average: {elapsed/len(queries):.2f} seconds per query")
    print_separator("-")
    print()


def demo_customization():
    """Demonstrate query customization options."""
    print_separator()
    print("DEMO 5: Query Customization")
    print_separator()
    print()
    
    # Initialize
    handler = QueryHandler(vector_store_dir="data/vector_store", k=3)
    handler.initialize()
    
    query = "What is Article 21?"
    
    # Test different temperature settings
    print(f"📝 Query: {query}")
    print()
    
    print("🧊 LOW TEMPERATURE (0.1) - More Factual:")
    print_separator("-")
    result1 = handler.query(query, temperature=0.1, max_tokens=500)
    print(result1['response'][:400] + "...")
    print()
    
    print()
    print("🔥 HIGHER TEMPERATURE (0.7) - More Creative:")
    print_separator("-")
    result2 = handler.query(query, temperature=0.7, max_tokens=500)
    print(result2['response'][:400] + "...")
    print()
    
    print_separator("-")
    print("Note: Temperature affects response style but both use same sources")
    print_separator("-")
    print()


def main():
    """Run all demos."""
    print()
    print("🏛️" * 35)
    print()
    print("         LexiQ RETRIEVAL SYSTEM - DEMO")
    print()
    print("🏛️" * 35)
    print()
    
    demos = [
        ("Basic Query", demo_basic_query),
        ("Metadata Access", demo_retrieval_with_metadata),
        ("Pure Search", demo_search_only),
        ("Batch Processing", demo_batch_queries),
        ("Customization", demo_customization)
    ]
    
    print("Available demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos) + 1}. Run all demos")
    print()
    
    try:
        choice = input("Select demo (1-6): ").strip()
        
        if choice == str(len(demos) + 1):
            # Run all demos
            for name, demo_func in demos:
                print()
                demo_func()
                input("Press Enter to continue to next demo...")
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            # Run selected demo
            _, demo_func = demos[int(choice) - 1]
            demo_func()
        else:
            print("Invalid choice. Running demo 1 (Basic Query)...")
            demo_basic_query()
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("\nMake sure you have:")
        print("  1. Run process_documents.py to create the vector store")
        print("  2. Configured AWS credentials for Bedrock")
        print("  3. Installed all requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()

