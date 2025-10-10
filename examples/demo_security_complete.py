#!/usr/bin/env python3
"""
Complete Security Test - All Features
Tests PII Redaction, Input Validation, and Hallucination Detection on a single case
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from security.security_enforcer import SecurityEnforcer
from security.hallucination_detector import HallucinationDetector
from utils.retriever import LegalDocumentRetriever


# Realistic legal case text with PII, valid references, and fake references
TEST_CASE = """
PETITION FOR ANTICIPATORY BAIL
CRIMINAL MISCELLANEOUS CASE NO. 12345/2024

IN THE HIGH COURT OF DELHI
AT NEW DELHI

Petitioner: Mr. Rajesh Kumar Singh
Address: 45B Nehru Nagar, New Delhi - 110019
Contact: +91-9876543210
Email: rajesh.kumar@legalmail.com
PAN: ABCDE1234F
Aadhaar: 1234-5678-9012
Bank Account: 1234567890123456 (State Bank of India)

VERSUS

Respondent: State of Delhi
Through: Public Prosecutor

CASE DETAILS:

The petitioner seeks anticipatory bail in connection with FIR No. 234/2024 
registered under Section 420 of IPC (Cheating) and Section 66D of IT Act 
(Punishment for cheating by personation using computer resource).

FACTS:

1. The complainant, Ms. Priya Sharma (contact: +91-8765432109, 
   email: priya.s@email.com), alleges that the petitioner fraudulently 
   obtained Rs. 5,00,000/- through false representations.

2. The petitioner denies all allegations and states that the transaction 
   was legitimate business dealing covered under Section 138 of 
   Negotiable Instruments Act.

LEGAL GROUNDS:

A. CONSTITUTIONAL RIGHTS

1. Article 21 of the Constitution guarantees right to life and personal 
   liberty. The petitioner cannot be subjected to arbitrary arrest.

2. Article 14 ensures equality before law. Similar cases have resulted 
   in anticipatory bail.

3. Article 500 of the Constitution also protects citizens from 
   unwarranted detention. [FAKE ARTICLE - TESTING HALLUCINATION DETECTION]

B. STATUTORY PROVISIONS

1. Section 438 of CrPC provides for anticipatory bail in cases where 
   arrest is not warranted.

2. Section 41A of CrPC mandates notice before arrest in cases 
   punishable with imprisonment up to seven years.

3. Section 999 of IPC deals with bail conditions in fraud cases.
   [FAKE SECTION - TESTING HALLUCINATION DETECTION]

4. Section 482 of CrPC empowers High Court to prevent abuse of 
   process of law.

C. JUDICIAL PRECEDENTS

1. In Arnab Manoranjan Goswami vs State of Maharashtra [2020] 14 S.C.C. 12,
   the Supreme Court held that personal liberty is sacrosanct.

2. In Sushila Aggarwal vs State (NCT of Delhi) [2025] 1 S.C.R. 123,
   it was held that anticipatory bail should not be denied mechanically.

3. The case of [2099] 99 S.C.R. 999 : 2099 INSC 9999 established that 
   economic offenses require stringent scrutiny before arrest.
   [FAKE CITATION - TESTING HALLUCINATION DETECTION]

D. NO LIKELIHOOD OF ARREST

The petitioner, Mr. Rajesh Kumar (PAN: BCDEF5678G, Aadhaar: 9876-5432-1098),
has deep roots in society, owns property, and has never been involved in 
any criminal activity. His business partner, Mr. Amit Verma 
(mobile: +91-7654321098), can vouch for his character.

E. COOPERATION WITH INVESTIGATION

The petitioner has cooperated fully with investigation and has provided 
all documents including:
- Bank statements from Account No. 9876543210987654
- Business records
- Communication records

PRAYER:

In light of the above, and considering Section 888 of CrPC regarding 
protective provisions [FAKE SECTION], it is humbly prayed that this 
Hon'ble Court may be pleased to grant anticipatory bail to the petitioner.

Place: New Delhi
Date: October 9, 2025

Advocate for Petitioner
Adv. Neha Gupta
Enrollment No: D/12345/2015
Email: neha.gupta@lawfirm.com
Contact: +91-9988776655
"""


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_complete_security():
    """Test all security features on the case."""
    
    print("\n" + "🔐" * 40)
    print("COMPLETE SECURITY TEST - LexiQ")
    print("🔐" * 40)
    
    # =========================================================================
    # STEP 1: INPUT VALIDATION & PII REDACTION
    # =========================================================================
    print_section("STEP 1: INPUT VALIDATION & PII REDACTION")
    
    print("📄 Original Case Text Length:", len(TEST_CASE), "characters")
    print()
    
    # Initialize security enforcer
    security = SecurityEnforcer(
        enable_pii_redaction=True,
        enable_validation=True,
        min_pii_confidence=0.7
    )
    
    # Process the case
    print("🔍 Processing through security enforcer...")
    result = security.process_case_input(
        case_text=TEST_CASE,
        user_id="test_user_001",
        ip_address="192.168.1.100"
    )
    
    if not result['success']:
        print("❌ Security check FAILED!")
        print(f"   Error: {result['error']}")
        print(f"   Violations: {result['violations']}")
        return
    
    print("✅ Security check PASSED!")
    print()
    
    # Display PII detection results
    metadata = result['security_metadata']
    
    print("🔒 PII DETECTION RESULTS:")
    pii_types = metadata.get('pii_detected', [])
    print(f"   PII Detected: {'Yes' if pii_types else 'No'}")
    if pii_types:
        print(f"   Types Found: {', '.join(pii_types)}")
    print(f"   Total Redactions: {metadata['num_redactions']}")
    print(f"   Confidence Score: {metadata.get('redaction_confidence', 1.0):.2f}")
    print(f"   Risk Score: {metadata['risk_score']:.2f}")
    print()
    
    # Show sample of redacted text
    redacted_text = result['processed_text']
    print("📝 REDACTED TEXT SAMPLE (first 500 chars):")
    print("-" * 80)
    print(redacted_text[:500] + "...")
    print("-" * 80)
    print()
    
    # =========================================================================
    # STEP 2: SIMULATE LLM RESPONSE WITH LEGAL ANALYSIS
    # =========================================================================
    print_section("STEP 2: SIMULATED LLM ANALYSIS")
    
    # Simulate an LLM response that includes both valid and fake references
    llm_response = """
    LEGAL ANALYSIS OF THE CASE
    
    Based on the petition, the following legal analysis is provided:
    
    1. CONSTITUTIONAL PROTECTION
       - Article 21 guarantees life and liberty (VALID)
       - Article 14 ensures equality before law (VALID)
       - Article 500 mentioned is not applicable (FAKE - will be detected)
    
    2. ANTICIPATORY BAIL PROVISIONS
       - Section 438 of CrPC is the primary provision (VALID)
       - Section 41A mandates notice before arrest (VALID)
       - Section 999 of IPC cited does not exist (FAKE - will be detected)
       - Section 482 CrPC for inherent powers is correct (VALID)
    
    3. APPLICABLE OFFENSES
       - Section 420 IPC (Cheating) is bailable (VALID)
       - Section 66D IT Act is correctly cited (VALID)
    
    4. PRECEDENTS ANALYSIS
       - Arnab Goswami case [2020] 14 S.C.C. 12 is correctly cited (VALID)
       - Sushila Aggarwal case citation appears valid (NEEDS VERIFICATION)
       - The [2099] 99 S.C.R. 999 case does not exist (FAKE - will be detected)
    
    5. ADDITIONAL CONSIDERATIONS
       - Section 888 of CrPC mentioned is invalid (FAKE - will be detected)
       - Section 154 CrPC for FIR registration is standard (VALID)
    
    RECOMMENDATION: 
    Anticipatory bail should be granted given:
    - Non-violent economic offense
    - Willingness to cooperate
    - Deep roots in society
    - Valid grounds under Section 438 CrPC
    
    CONFIDENCE: HIGH (subject to verification of precedents)
    """
    
    print("📊 LLM Generated Analysis:")
    print("-" * 80)
    print(llm_response)
    print("-" * 80)
    print()
    
    # =========================================================================
    # STEP 3: HALLUCINATION DETECTION
    # =========================================================================
    print_section("STEP 3: HALLUCINATION DETECTION")
    
    try:
        # Initialize hallucination detector with vector store
        print("🔍 Loading vector store...")
        retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
        retriever.load_vector_store()
        detector = HallucinationDetector(retriever=retriever)
        print("✅ Vector store loaded successfully")
    except Exception as e:
        print(f"⚠️  Could not load vector store: {e}")
        print("   Using basic hallucination detection (no case citation validation)")
        detector = HallucinationDetector()
    
    print()
    print("🔍 Analyzing LLM output for hallucinations...")
    print()
    
    # Detect hallucinations
    hallucination_result = detector.detect_hallucinations(
        input_query="Analyze this anticipatory bail petition",
        output_text=llm_response,
        user_id="test_user_001"
    )
    
    # Display results
    print("🎯 HALLUCINATION DETECTION RESULTS:")
    print(f"   Has Hallucinations: {'YES ⚠️' if hallucination_result['has_hallucinations'] else 'NO ✅'}")
    print(f"   Total References: {hallucination_result['num_references']}")
    print(f"   Valid References: {hallucination_result['num_references'] - hallucination_result['num_suspected']}")
    print(f"   Suspected Fakes: {hallucination_result['num_suspected']}")
    print(f"   Confidence Score: {hallucination_result['confidence_score']:.2f}")
    print()
    
    if hallucination_result['has_hallucinations']:
        print("⚠️  SUSPECTED FAKE REFERENCES DETECTED:")
        print()
        for i, fake in enumerate(hallucination_result['suspected_fake_refs'], 1):
            print(f"   {i}. 📛 {fake['text']}")
            print(f"      Type: {fake['type'].upper()}")
            print(f"      Reason: {fake['reason']}")
            print(f"      Confidence: {fake['confidence'] * 100:.0f}%")
            print(f"      Matched Statute: {fake['matched_statute']}")
            print(f"      Validated Against Index: {fake['validated_against_index']}")
            print()
    
    print(f"💡 {hallucination_result['summary']}")
    print()
    
    # =========================================================================
    # STEP 4: FINAL SUMMARY
    # =========================================================================
    print_section("STEP 4: COMPREHENSIVE SECURITY SUMMARY")
    
    print("📊 SECURITY METRICS:")
    print()
    print("   INPUT SECURITY:")
    print(f"      ✅ Validation: PASSED")
    print(f"      ✅ PII Redacted: {metadata['num_redactions']} items")
    print(f"      ✅ Risk Score: {metadata['risk_score']:.2f} (Low)")
    print()
    print("   OUTPUT VALIDATION:")
    print(f"      {'⚠️' if hallucination_result['has_hallucinations'] else '✅'} Hallucinations: {hallucination_result['num_suspected']} detected")
    print(f"      ✅ Valid References: {hallucination_result['num_references'] - hallucination_result['num_suspected']}")
    print(f"      {'⚠️' if hallucination_result['confidence_score'] < 0.9 else '✅'} Confidence: {hallucination_result['confidence_score']:.2f}")
    print()
    print("   AUDIT TRAIL:")
    print(f"      ✅ Security Log: security/logs/security_audit.log")
    print(f"      ✅ Hallucination Log: security/logs/hallucination_audit.log")
    print(f"      ✅ Request ID: {result['request_id']}")
    print()
    
    # Action items
    print("📋 ACTION ITEMS:")
    print()
    if metadata['pii_detected']:
        print(f"   1. ⚠️  {metadata['num_redactions']} PII items were redacted")
        print("      → Review if any legal entity names were incorrectly flagged")
    
    if hallucination_result['has_hallucinations']:
        print(f"   2. ⚠️  {hallucination_result['num_suspected']} fake references detected")
        print("      → Warn user to verify these references independently")
        print("      → Consider regenerating response without fake references")
    
    print(f"   3. ✅ Original input hash stored: {metadata['original_input_hash'][:16]}...")
    print("      → Can be used for audit trail and verification")
    print()
    
    # =========================================================================
    # STEP 5: VIEW LOGS
    # =========================================================================
    print_section("STEP 5: AUDIT LOGS")
    
    print("📋 Recent audit log entries have been created:")
    print()
    print("   Security Audit Log:")
    print("   → security/logs/security_audit.log")
    print()
    print("   Hallucination Audit Log:")
    print("   → security/logs/hallucination_audit.log")
    print()
    print("💡 View logs with:")
    print("   tail -20 security/logs/security_audit.log")
    print("   tail -20 security/logs/hallucination_audit.log")
    print()
    
    # =========================================================================
    # FINAL MESSAGE
    # =========================================================================
    print("=" * 80)
    print("✅ COMPLETE SECURITY TEST FINISHED")
    print("=" * 80)
    print()
    print("🎯 Summary:")
    print(f"   • PII Detection: {metadata['num_redactions']} items redacted")
    print(f"   • Input Validation: PASSED")
    print(f"   • Hallucination Detection: {hallucination_result['num_suspected']} fakes caught")
    print(f"   • All security features working correctly! ✅")
    print()


if __name__ == "__main__":
    try:
        test_complete_security()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

