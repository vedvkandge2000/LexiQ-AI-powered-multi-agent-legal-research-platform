#!/usr/bin/env python3
"""
Demo: Case Deduplication
Shows the difference between deduplicated and non-deduplicated search results.
"""

from utils.case_similarity import CaseSimilarityAnalyzer


def main():
    print("=" * 80)
    print("DEMO: Case Deduplication in Search Results")
    print("=" * 80)
    print()
    print("This demo shows how deduplication works when a case has multiple chunks.")
    print()
    
    # Initialize analyzer
    analyzer = CaseSimilarityAnalyzer()
    analyzer.initialize()
    
    # Search query
    search_text = "freedom of speech and reasonable restrictions under Article 19"
    k = 10
    
    print("=" * 80)
    print(f"Search Query: {search_text}")
    print(f"Requested: {k} results")
    print("=" * 80)
    print()
    
    # Test 1: WITH deduplication (default) - returns unique cases
    print("🔹 TEST 1: WITH DEDUPLICATION (deduplicate=True)")
    print("-" * 80)
    print(f"Expected: {k} UNIQUE CASES (one result per case)")
    print()
    
    cases_dedup = analyzer.find_similar_cases_only(
        case_text=search_text,
        k=k,
        deduplicate=True
    )
    
    print()
    print(f"Results: {len(cases_dedup)} unique cases")
    print()
    
    for i, case in enumerate(cases_dedup[:5], 1):  # Show first 5
        print(f"{i}. {case['case_title']}")
        print(f"   Citation: {case['citation']}")
        print(f"   Page: {case['page_number']}, Section: {case['section'][:50]}...")
        print(f"   Score: {case['similarity_score']:.4f}")
        print()
    
    if len(cases_dedup) > 5:
        print(f"... and {len(cases_dedup) - 5} more unique cases")
    print()
    
    # Test 2: WITHOUT deduplication - returns chunks (may have duplicates)
    print()
    print("=" * 80)
    print("🔹 TEST 2: WITHOUT DEDUPLICATION (deduplicate=False)")
    print("-" * 80)
    print(f"Expected: {k} CHUNKS (may include multiple chunks from same case)")
    print()
    
    chunks = analyzer.find_similar_cases_only(
        case_text=search_text,
        k=k,
        deduplicate=False
    )
    
    print()
    print(f"Results: {len(chunks)} chunks")
    print()
    
    # Count unique cases in non-deduplicated results
    unique_case_numbers = set(c['case_number'] for c in chunks)
    
    print(f"⚠️  Note: These {len(chunks)} chunks represent only {len(unique_case_numbers)} unique cases!")
    print()
    
    for i, chunk in enumerate(chunks[:5], 1):  # Show first 5
        print(f"{i}. {chunk['case_title']}")
        print(f"   Citation: {chunk['citation']}")
        print(f"   Page: {chunk['page_number']}, Section: {chunk['section'][:50]}...")
        print(f"   Score: {chunk['similarity_score']:.4f}")
        print()
    
    if len(chunks) > 5:
        print(f"... and {len(chunks) - 5} more chunks")
    print()
    
    # Test 3: Get multiple chunks per case (grouped)
    print()
    print("=" * 80)
    print("🔹 TEST 3: MULTIPLE CHUNKS PER CASE (find_similar_cases_with_chunks)")
    print("-" * 80)
    print("Expected: Unique cases with their top relevant chunks grouped together")
    print()
    
    cases_with_chunks = analyzer.find_similar_cases_with_chunks(
        case_text=search_text,
        k_cases=5,  # 5 unique cases
        max_chunks_per_case=3  # Up to 3 chunks per case
    )
    
    print()
    total_chunks = sum(len(case['chunks']) for case in cases_with_chunks)
    print(f"Results: {len(cases_with_chunks)} unique cases with {total_chunks} total chunks")
    print()
    
    for i, case in enumerate(cases_with_chunks, 1):
        print(f"{i}. {case['case_title']}")
        print(f"   Citation: {case['citation']}")
        print(f"   Best Score: {case['best_score']:.4f}")
        print(f"   PDF: {case['s3_url'][:60]}..." if case['s3_url'] else "   No PDF")
        print(f"   Relevant Chunks ({len(case['chunks'])}):")
        
        for j, chunk in enumerate(case['chunks'], 1):
            print(f"      {j}. Page {chunk['page_number']}, Section: {chunk['section'][:40]}...")
            print(f"         Score: {chunk['similarity_score']:.4f}")
        print()
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Three ways to search:")
    print()
    print("1. ✅ DEDUPLICATED (default)")
    print(f"   - Request k={k}")
    print(f"   - Get {len(cases_dedup)} unique cases")
    print("   - Best use: When you want diverse case coverage")
    print()
    print("2. 📄 NON-DEDUPLICATED")
    print(f"   - Request k={k}")
    print(f"   - Get {len(chunks)} chunks from {len(unique_case_numbers)} cases")
    print("   - Best use: When you want all relevant excerpts")
    print()
    print("3. 📚 GROUPED BY CASE")
    print("   - Request k_cases=5, max_chunks=3")
    print(f"   - Get {len(cases_with_chunks)} cases with {total_chunks} chunks")
    print("   - Best use: When you want multiple excerpts per case, grouped")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()

