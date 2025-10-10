#!/usr/bin/env python3
"""
Quick test to verify judge extraction is working
"""

from utils.retriever import LegalDocumentRetriever

# Load vector store
retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
retriever.load_vector_store()

print("=" * 70)
print("Testing Judge Extraction from Vector Store")
print("=" * 70)
print()

# Get a sample of documents
sample_query = "case law"
results = retriever.retrieve(sample_query, k=5)

print(f"Checking {len(results)} sample documents:\n")

judges_found = 0
for i, doc in enumerate(results, 1):
    metadata = doc.metadata
    print(f"{i}. Case: {metadata.get('case_title', 'Unknown')[:50]}...")
    print(f"   Citation: {metadata.get('citation', 'N/A')}")
    
    if 'judges' in metadata and metadata['judges']:
        judges = metadata['judges']
        if isinstance(judges, list):
            print(f"   ✅ Judges: {', '.join(judges)}")
            judges_found += 1
        else:
            print(f"   ✅ Judge: {judges}")
            judges_found += 1
    else:
        print(f"   ⚠️  No judges found in metadata")
    print()

print("=" * 70)
print(f"Summary: {judges_found}/{len(results)} documents have judge metadata")
print("=" * 70)

if judges_found > 0:
    print("\n✅ SUCCESS: Judge extraction is working!")
else:
    print("\n⚠️  WARNING: No judges found. Check PDF format.")

