#!/usr/bin/env python3
"""
Test a sample case with the LexiQ system
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sample_test_cases import get_sample_case
from utils.case_similarity import CaseSimilarityAnalyzer

def test_sample_case():
    print("=" * 80)
    print("TESTING SAMPLE CASE WITH LEXIQ SYSTEM")
    print("=" * 80)
    
    # Get a sample case
    case_text = get_sample_case('constitutional_rights')
    print("Testing Case: Fundamental Rights Violation")
    print("-" * 80)
    print(case_text)
    print("-" * 80)
    
    try:
        # Initialize the analyzer
        print("\n1. Initializing Case Similarity Analyzer...")
        analyzer = CaseSimilarityAnalyzer()
        analyzer.initialize()
        print("✅ Analyzer initialized successfully!")
        
        # Test case analysis
        print("\n2. Analyzing case for similar precedents...")
        result = analyzer.analyze_case_from_text(
            case_description=case_text,
            k=3,  # Get top 3 similar cases
            max_tokens=1000,
            temperature=0.3
        )
        
        print("✅ Analysis completed!")
        
        # Show results
        print("\n3. Results:")
        print(f"Similar cases found: {len(result.get('similar_cases', []))}")
        
        if 'similar_cases' in result:
            for i, case in enumerate(result['similar_cases'][:3]):
                print(f"\n--- Similar Case {i+1} ---")
                print(f"Citation: {case.get('citation', 'N/A')}")
                print(f"Title: {case.get('case_title', 'N/A')}")
                print(f"Page: {case.get('page_number', 'N/A')}")
                print(f"Similarity: {case.get('similarity_score', 'N/A')}")
                print(f"Content: {case.get('content', '')[:200]}...")
        
        # Show AI analysis
        if 'analysis' in result:
            print(f"\n4. AI Analysis:")
            print(result['analysis'])
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sample_case()
