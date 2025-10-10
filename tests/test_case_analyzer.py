#!/usr/bin/env python3
"""
Test script for LexiQ Case Similarity Analyzer.
"""

from utils.case_similarity import CaseSimilarityAnalyzer


def test_text_analysis():
    """Test case analysis from text description."""
    
    print("=" * 70)
    print("TEST 1: Case Analysis from Text Description")
    print("=" * 70)
    print()
    
    # Initialize analyzer
    analyzer = CaseSimilarityAnalyzer(vector_store_dir="data/vector_store")
    analyzer.initialize()
    
    # Sample case description
    sample_case = """
    Case Title: XYZ Corporation vs. State of Maharashtra
    
    Facts:
    The petitioner, XYZ Corporation, challenges the validity of a state law that 
    restricts freedom of speech and expression by imposing prior censorship on 
    digital publications. The petitioner argues this violates Article 19(1)(a) of 
    the Constitution.
    
    Legal Issues:
    1. Whether prior censorship on digital media violates fundamental rights
    2. Whether the restriction is reasonable under Article 19(2)
    3. The balance between free speech and public order
    
    Petitioner's Arguments:
    - The law imposes unreasonable restrictions on freedom of expression
    - Digital media should have the same protections as traditional press
    - The censorship mechanism lacks clear guidelines and is arbitrary
    
    Relief Sought:
    Declaration that the impugned provisions are unconstitutional and violate 
    Article 19(1)(a) of the Constitution of India.
    """
    
    print("Sample Case Description:")
    print("-" * 70)
    print(sample_case)
    print("-" * 70)
    print()
    
    # Analyze
    result = analyzer.analyze_case_from_text(sample_case, k=3)
    
    # Display results
    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    print()
    print(result["analysis"])
    print()
    
    print("=" * 70)
    print(f"Similar Cases Found: {result['num_similar_cases']}")
    print("=" * 70)
    print()
    
    for i, case in enumerate(result['similar_cases'], 1):
        print(f"{i}. {case['case_title']}")
        print(f"   Citation: {case['citation']}")
        print(f"   Case Number: {case['case_number']}")
        print(f"   Page Number: {case.get('page_number', 'N/A')}")
        print(f"   PDF: {case['s3_url'] if case['s3_url'] else 'Not available'}")
        print()


def test_quick_search():
    """Test quick similarity search."""
    
    print("\n" + "=" * 70)
    print("TEST 2: Quick Similarity Search")
    print("=" * 70)
    print()
    
    # Initialize analyzer
    analyzer = CaseSimilarityAnalyzer(vector_store_dir="data/vector_store")
    analyzer.initialize()
    
    # Search query
    search_text = "freedom of speech and reasonable restrictions"
    
    print(f"Search Query: {search_text}")
    print()
    
    # Find similar cases
    similar_cases = analyzer.find_similar_cases_only(
        case_text=search_text,
        k=5,
        with_scores=True
    )
    
    print("=" * 70)
    print(f"SEARCH RESULTS ({len(similar_cases)} cases)")
    print("=" * 70)
    print()
    
    for i, case in enumerate(similar_cases, 1):
        score = case.get('similarity_score', 0)
        print(f"{i}. {case['case_title']}")
        print(f"   Citation: {case['citation']}")
        print(f"   Page Number: {case.get('page_number', 'N/A')}")
        print(f"   Similarity Score: {score:.4f}")
        print(f"   Section: {case.get('section', 'N/A')}")
        print(f"   Preview: {case['content_preview'][:200]}...")
        print()


def test_pdf_analysis():
    """Test case analysis from PDF (requires a PDF file)."""
    
    print("\n" + "=" * 70)
    print("TEST 3: Case Analysis from PDF")
    print("=" * 70)
    print()
    
    # Check if test PDF exists
    test_pdf = "data/pdfs/1.pdf"
    
    import os
    if not os.path.exists(test_pdf):
        print(f"⚠️  Test PDF not found: {test_pdf}")
        print("Skipping PDF analysis test.")
        return
    
    # Initialize analyzer
    analyzer = CaseSimilarityAnalyzer(vector_store_dir="data/vector_store")
    analyzer.initialize()
    
    # Analyze PDF
    result = analyzer.analyze_case_from_pdf(test_pdf, k=3)
    
    # Display results
    print("\n" + "=" * 70)
    print("PDF METADATA")
    print("=" * 70)
    if 'pdf_metadata' in result:
        for key, value in result['pdf_metadata'].items():
            print(f"{key}: {value}")
    print()
    
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print(result["analysis"][:1000] + "...")  # First 1000 chars
    print()
    
    print("=" * 70)
    print(f"Similar Cases: {result['num_similar_cases']}")
    print("=" * 70)


def main():
    """Run all tests."""
    print("\n")
    print("🏛️" * 35)
    print()
    print("    LexiQ CASE SIMILARITY ANALYZER - TEST SUITE")
    print()
    print("🏛️" * 35)
    print("\n")
    
    try:
        # Test 1: Text analysis
        test_text_analysis()
        
        input("\nPress Enter to continue to next test...")
        
        # Test 2: Quick search
        test_quick_search()
        
        input("\nPress Enter to continue to next test...")
        
        # Test 3: PDF analysis (optional)
        test_pdf_analysis()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted.")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

