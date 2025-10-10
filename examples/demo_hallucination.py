#!/usr/bin/env python3
"""
Demo: Hallucination Detection
Shows how to validate legal references in LLM outputs
"""

from security.hallucination_detector import HallucinationDetector
from utils.retriever import LegalDocumentRetriever


def demo_basic():
    """Basic hallucination detection demo."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Hallucination Detection")
    print("="*70 + "\n")
    
    detector = HallucinationDetector()
    
    # Fake LLM output with invalid references
    llm_output = """
    Based on legal analysis, the following laws apply:
    
    1. Section 302 of IPC (Murder) - VALID
    2. Section 999 of IPC - FAKE (doesn't exist)
    3. Article 21 of Constitution (Right to Life) - VALID
    4. Article 500 of Constitution - FAKE (doesn't exist)
    """
    
    print("📝 LLM Output:")
    print(llm_output)
    print()
    
    # Detect hallucinations
    result = detector.detect_hallucinations(
        input_query="What laws apply to this case?",
        output_text=llm_output,
        user_id="demo_user"
    )
    
    # Display results
    if result['has_hallucinations']:
        print("⚠️  HALLUCINATION DETECTED!\n")
        print(f"   Total References: {result['num_references']}")
        print(f"   Suspected Fakes: {result['num_suspected']}")
        print(f"   Confidence: {result['confidence_score']}\n")
        
        print("❌ Suspected Fake References:\n")
        for i, fake in enumerate(result['suspected_fake_refs'], 1):
            print(f"   {i}. {fake['text']}")
            print(f"      Reason: {fake['reason']}")
            print(f"      Confidence: {fake['confidence']}\n")
    else:
        print("✅ All references validated successfully!")
    
    print(result['summary'])
    print()


def demo_with_vector_store():
    """Demo with vector store for case citation validation."""
    print("\n" + "="*70)
    print("DEMO 2: Case Citation Validation (with Vector Store)")
    print("="*70 + "\n")
    
    try:
        # Initialize with vector store
        retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
        retriever.load_vector_store()
        detector = HallucinationDetector(retriever=retriever)
        print("✓ Vector store loaded\n")
    except:
        print("⚠️  Vector store not available, using basic mode\n")
        detector = HallucinationDetector()
    
    # LLM output with case citations
    llm_output = """
    Relevant precedents:
    
    1. In [2025] 9 S.C.R. 585 : 2025 INSC 1097 (real case from our DB)
    2. In [2099] 99 S.C.R. 999 : 2099 INSC 9999 (fake citation)
    """
    
    print("📝 LLM Output:")
    print(llm_output)
    print()
    
    result = detector.detect_hallucinations(
        input_query="Find similar cases",
        output_text=llm_output,
        user_id="demo_user"
    )
    
    if result['has_hallucinations']:
        print(f"⚠️  {result['num_suspected']} suspected fake citation(s)\n")
        for fake in result['suspected_fake_refs']:
            if "not found" in fake['reason'].lower():
                print(f"   ❌ {fake['text']}")
                print(f"      {fake['reason']}\n")
    print()


def demo_real_world():
    """Real-world scenario with mixed valid/invalid references."""
    print("\n" + "="*70)
    print("DEMO 3: Real-World Scenario")
    print("="*70 + "\n")
    
    detector = HallucinationDetector()
    
    # Realistic LLM output
    llm_output = """
    LEGAL ANALYSIS
    
    The petitioner's case primarily relies on:
    
    1. Section 498A of IPC (Cruelty by husband or relatives)
       This provision is applicable as alleged facts constitute cruelty.
       
    2. Article 14 of the Constitution (Equality before law)
       Petitioner argues discriminatory treatment.
       
    3. Section 154 of CrPC (FIR registration)
       Police failed to register FIR promptly.
       
    4. Section 888 of IPC (Non-existent provision)
       This section supposedly deals with bail conditions.
       
    5. Section 376A of IPC (Punishment for rape causing death)
       Aggravated circumstances present in this case.
    
    RECOMMENDATION: Petition has merit under valid provisions.
    WARNING: Section 888 reference appears erroneous.
    """
    
    print("📝 LLM Generated Legal Analysis:")
    print(llm_output)
    print()
    
    result = detector.detect_hallucinations(
        input_query="Analyze this petition",
        output_text=llm_output,
        user_id="lawyer_001"
    )
    
    print("🔍 VALIDATION RESULTS\n")
    print(f"   Total References Found: {result['num_references']}")
    print(f"   Valid References: {result['num_references'] - result['num_suspected']}")
    print(f"   Suspected Fakes: {result['num_suspected']}")
    print(f"   Overall Confidence: {result['confidence_score']}\n")
    
    if result['has_hallucinations']:
        print("⚠️  ATTENTION: Some references could not be validated!\n")
        print("   Please verify the following independently:\n")
        
        for fake in result['suspected_fake_refs']:
            print(f"   ❌ {fake['text']}")
            print(f"      Issue: {fake['reason']}")
            print(f"      Confidence: {fake['confidence'] * 100:.0f}%\n")
        
        print("   ✅ All other references validated successfully.")
    
    print()
    print(f"💡 {result['summary']}")
    print()


def main():
    """Run all demos."""
    print("\n")
    print("="*70)
    print("🔍 LexiQ Hallucination Detection - Demo")
    print("="*70)
    
    try:
        demo_basic()
        demo_with_vector_store()
        demo_real_world()
        
        print("="*70)
        print("✅ Demo Complete")
        print("="*70)
        print()
        print("💡 Key Takeaways:")
        print("   • Detects fake IPC sections (e.g., Section 999)")
        print("   • Detects fake Constitution articles (e.g., Article 500)")
        print("   • Validates case citations against vector store")
        print("   • Provides confidence scores and reasons")
        print("   • Logs all suspected hallucinations")
        print()
        print("📋 Check logs: security/logs/hallucination_audit.log")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

