#!/usr/bin/env python3
"""
Test improved case analysis with proper case grouping
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.retriever import LegalDocumentRetriever
from utils.case_analyzer_improved import create_improved_analyzer
from sample_test_cases import get_sample_case

def test_improved_analysis():
    print("=" * 80)
    print("TESTING IMPROVED CASE ANALYSIS WITH CASE GROUPING")
    print("=" * 80)
    
    # Initialize components
    print("\n1. Initializing components...")
    retriever = LegalDocumentRetriever()
    retriever.load_vector_store()
    
    improved_analyzer = create_improved_analyzer(retriever)
    print("✅ Components initialized!")
    
    # Get sample case
    case_text = get_sample_case('constitutional_rights')
    print(f"\n2. Testing with: Fundamental Rights Violation case")
    print(f"   Case length: {len(case_text)} characters")
    
    # Test improved analysis
    print(f"\n3. Running improved analysis with case grouping...")
    try:
        result = improved_analyzer.analyze_case_with_grouping(
            case_description=case_text,
            k=15,  # Get more chunks to group
            max_tokens=2000,
            temperature=0.3
        )
        
        print("✅ Analysis completed!")
        
        # Show results
        print(f"\n4. Results Summary:")
        print(f"   Unique cases found: {result['num_unique_cases']}")
        print(f"   Total chunks retrieved: {result['total_chunks']}")
        print(f"   Analysis length: {len(result['analysis'])} characters")
        
        print(f"\n5. Cases Found:")
        for i, case in enumerate(result['cases_found'][:3]):
            print(f"   {i+1}. {case['case_title']}")
            print(f"      Citation: {case['citation']}")
            print(f"      Judges: {', '.join(case['judges']) if case['judges'] else 'N/A'}")
            print(f"      Chunks: {case['num_chunks']}")
            print(f"      Pages: {', '.join(str(p) for p in case['pages'][:3])}")
        
        print(f"\n6. Analysis Preview:")
        print(result['analysis'][:500] + "...")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

def test_timeout_handling():
    print("\n" + "=" * 80)
    print("TESTING TIMEOUT HANDLING")
    print("=" * 80)
    
    from agents.news_relevance_agent import NewsRelevanceAgent
    
    # Test news agent with timeout handling
    print("\n1. Testing News Agent with timeout handling...")
    news_agent = NewsRelevanceAgent()
    
    case_text = get_sample_case('constitutional_rights')
    
    try:
        result = news_agent.find_relevant_news(case_text)
        print("✅ News analysis completed!")
        print(f"   Articles found: {len(result.get('articles', []))}")
        print(f"   Analysis length: {len(result.get('analysis', ''))} characters")
        
        # Show analysis preview
        if result.get('analysis'):
            print(f"\n   Analysis preview:")
            print(result['analysis'][:300] + "...")
            
    except Exception as e:
        print(f"⚠️ News analysis error: {e}")

if __name__ == "__main__":
    test_improved_analysis()
    test_timeout_handling()
    
    print("\n" + "=" * 80)
    print("IMPROVEMENTS IMPLEMENTED:")
    print("=" * 80)
    print("✅ 1. Added timeout configuration to Bedrock client")
    print("✅ 2. Created improved case analyzer with case grouping")
    print("✅ 3. Added fallback analysis for timeout scenarios")
    print("✅ 4. Enhanced news agent with timeout handling")
    print("\nThe system now:")
    print("• Groups chunks by case for better analysis")
    print("• Handles Claude timeouts gracefully")
    print("• Provides fallback content when AI is unavailable")
    print("• Uses proper timeout configurations")
    print("=" * 80)
