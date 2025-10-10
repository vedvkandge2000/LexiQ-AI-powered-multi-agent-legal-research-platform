#!/usr/bin/env python3
"""
Check what cases are in the database to create relevant test cases
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.retriever import LegalDocumentRetriever

def main():
    print("=" * 80)
    print("CHECKING DATABASE CONTENT")
    print("=" * 80)
    
    try:
        retriever = LegalDocumentRetriever()
        retriever.load_vector_store()
        
        # Try to get some sample cases
        print("\n1. Testing basic search...")
        results = retriever.retrieve(
            query="constitutional rights",
            k=5
        )
        
        print(f"Found {len(results)} results")
        
        # Show metadata from results
        for i, result in enumerate(results[:3]):
            print(f"\n--- Result {i+1} ---")
            metadata = result.metadata
            print(f"Title: {metadata.get('title', 'N/A')}")
            print(f"Citation: {metadata.get('citation', 'N/A')}")
            print(f"Date: {metadata.get('date', 'N/A')}")
            print(f"Court: {metadata.get('court', 'N/A')}")
            print(f"Judges: {metadata.get('judges', 'N/A')}")
            print(f"Page: {metadata.get('page_number', 'N/A')}")
            
            # Show a snippet of content
            content = result.page_content[:200] + "..." if len(result.page_content) > 200 else result.page_content
            print(f"Content: {content}")
        
        # Try different search terms
        print("\n" + "=" * 80)
        print("2. Testing different search terms...")
        
        search_terms = [
            "fundamental rights",
            "criminal law",
            "civil procedure",
            "contract dispute",
            "constitutional validity",
            "anticipatory bail",
            "right to life",
            "freedom of speech"
        ]
        
        for term in search_terms:
            try:
                results = retriever.retrieve(term, k=2)
                print(f"\n'{term}': Found {len(results)} results")
                if results:
                    title = results[0].metadata.get('title', 'No title')
                    print(f"  Top result: {title[:80]}...")
            except Exception as e:
                print(f"'{term}': Error - {e}")
        
    except Exception as e:
        print(f"Error initializing retriever: {e}")
        print("\nTrying alternative approach...")
        
        # Try to check if vector store files exist
        vector_files = [
            "data/vector_store/index.faiss",
            "data/vector_store/index.pkl"
        ]
        
        for file_path in vector_files:
            if Path(file_path).exists():
                print(f"✅ Found: {file_path}")
            else:
                print(f"❌ Missing: {file_path}")

if __name__ == "__main__":
    main()
