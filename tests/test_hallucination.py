#!/usr/bin/env python3
"""
Test Hallucination Detection
Demonstrates detection of fake precedents, articles, and statutes.
"""

from security.hallucination_detector import HallucinationDetector
from utils.retriever import LegalDocumentRetriever


def test_valid_statutes():
    """Test with valid statutory references."""
    print("=" * 70)
    print("TEST 1: VALID STATUTES")
    print("=" * 70)
    print()
    
    detector = HallucinationDetector()
    
    output_text = """
    Based on the precedents, Section 498A of IPC and Article 21 of the Constitution 
    are relevant. The case also involves Section 154 of CrPC and Section 115 of CPC.
    """
    
    print("LLM Output:")
    print(output_text)
    print()
    
    result = detector.detect_hallucinations(
        input_query="What are relevant laws?",
        output_text=output_text,
        user_id="test_user_001"
    )
    
    print(f"Has Hallucinations: {result['has_hallucinations']}")
    print(f"References Found: {result['num_references']}")
    print(f"Suspected Fakes: {result['num_suspected']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Summary: {result['summary']}")
    print()


def test_fake_statutes():
    """Test with fake statutory references."""
    print("=" * 70)
    print("TEST 2: FAKE STATUTES")
    print("=" * 70)
    print()
    
    detector = HallucinationDetector()
    
    output_text = """
    The case involves Section 999 of IPC (which does not exist) and 
    Article 500 of the Constitution (also invalid). Section 600 of CrPC 
    is also relevant.
    """
    
    print("LLM Output (with fake sections):")
    print(output_text)
    print()
    
    result = detector.detect_hallucinations(
        input_query="What laws apply?",
        output_text=output_text,
        user_id="test_user_002"
    )
    
    print(f"⚠️  Has Hallucinations: {result['has_hallucinations']}")
    print(f"References Found: {result['num_references']}")
    print(f"Suspected Fakes: {result['num_suspected']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Summary: {result['summary']}")
    print()
    
    if result['suspected_fake_refs']:
        print("Suspected Fake References:")
        for i, fake in enumerate(result['suspected_fake_refs'], 1):
            print(f"\n{i}. {fake['text']}")
            print(f"   Type: {fake['type']}")
            print(f"   Reason: {fake['reason']}")
            print(f"   Confidence: {fake['confidence']}")
            print(f"   Matched Statute: {fake['matched_statute']}")
    print()


def test_case_citations():
    """Test with case citations."""
    print("=" * 70)
    print("TEST 3: CASE CITATIONS")
    print("=" * 70)
    print()
    
    # Initialize with vector store for case validation
    try:
        retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
        retriever.load_vector_store()
        detector = HallucinationDetector(retriever=retriever)
        print("✓ Vector store loaded for citation validation")
    except:
        detector = HallucinationDetector()
        print("⚠️  Vector store not available, citations won't be validated")
    
    print()
    
    # Test with real citation from our database
    output_text = """
    In the case of [2025] 9 S.C.R. 585 : 2025 INSC 1097, the Supreme Court held...
    However, in [2099] 99 S.C.R. 999 : 2099 INSC 9999 (fake citation), it was argued...
    """
    
    print("LLM Output:")
    print(output_text)
    print()
    
    result = detector.detect_hallucinations(
        input_query="Find similar cases",
        output_text=output_text,
        user_id="test_user_003"
    )
    
    print(f"Has Hallucinations: {result['has_hallucinations']}")
    print(f"References Found: {result['num_references']}")
    print(f"Suspected Fakes: {result['num_suspected']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Summary: {result['summary']}")
    
    if result['suspected_fake_refs']:
        print("\nSuspected Fake References:")
        for i, fake in enumerate(result['suspected_fake_refs'], 1):
            print(f"\n{i}. {fake['text']}")
            print(f"   Reason: {fake['reason']}")
            print(f"   Validated Against Index: {fake['validated_against_index']}")
    print()


def test_mixed_references():
    """Test with mix of valid and invalid references."""
    print("=" * 70)
    print("TEST 4: MIXED VALID & INVALID")
    print("=" * 70)
    print()
    
    detector = HallucinationDetector()
    
    output_text = """
    The analysis is based on:
    1. Section 302 of IPC (Murder - valid)
    2. Article 14 of Constitution (Equality - valid)
    3. Section 888 of IPC (does not exist - FAKE)
    4. Section 376A of IPC (Punishment for rape causing death - valid)
    5. Article 450 of Constitution (does not exist - FAKE)
    6. Section 154 of CrPC (FIR - valid)
    """
    
    print("LLM Output:")
    print(output_text)
    print()
    
    result = detector.detect_hallucinations(
        input_query="Analyze this case",
        output_text=output_text,
        user_id="test_user_004"
    )
    
    print(f"⚠️  Has Hallucinations: {result['has_hallucinations']}")
    print(f"Total References: {result['num_references']}")
    print(f"Valid References: {result['num_references'] - result['num_suspected']}")
    print(f"Suspected Fakes: {result['num_suspected']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"\n{result['summary']}")
    
    if result['suspected_fake_refs']:
        print("\n❌ Suspected Fake References:")
        for i, fake in enumerate(result['suspected_fake_refs'], 1):
            print(f"\n{i}. {fake['text']}")
            print(f"   Reason: {fake['reason']}")
            print(f"   Confidence: {fake['confidence']}")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("=" * 70)
    print("🔍 LexiQ Hallucination Detector - Test Suite")
    print("=" * 70)
    print()
    
    try:
        test_valid_statutes()
        test_fake_statutes()
        test_case_citations()
        test_mixed_references()
        
        print("=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        print()
        print("Check security/logs/hallucination_audit.log for detected hallucinations")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

