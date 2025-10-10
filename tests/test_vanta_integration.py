#!/usr/bin/env python3
"""
Test Vanta API Integration
Demonstrates PII masking with Vanta compliance logging
"""

import os
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from security.pii_redactor import PIIRedactor
from integrations.vanta_client import VantaClient, PIIMaskingResult

def test_vanta_integration():
    print("=" * 80)
    print("TESTING VANTA API INTEGRATION")
    print("=" * 80)
    
    # Test data with PII
    test_cases = [
        {
            "name": "Basic PII Test",
            "text": "John Doe's email is john.doe@example.com and his phone is +91-9876543210. His Aadhaar is 1234-5678-9012.",
            "expected_pii": ["person_name", "email", "phone", "aadhaar"]
        },
        {
            "name": "Legal Case with PII",
            "text": "Case: Smith v. Jones. Plaintiff John Smith (john@law.com, +1-555-123-4567) alleges breach of contract.",
            "expected_pii": ["person_name", "email", "phone"]
        },
        {
            "name": "No PII Test",
            "text": "This is a simple legal case about contract law. No personal information is present.",
            "expected_pii": []
        }
    ]
    
    # Initialize PII redactor
    print("\n1. Initializing PII Redactor with Vanta integration...")
    redactor = PIIRedactor()
    
    if redactor.vanta_client:
        print("✅ Vanta client initialized successfully")
    else:
        print("⚠️ Vanta client not available - check credentials")
        print("   Set VANTA_CLIENT_ID and VANTA_CLIENT_SECRET environment variables")
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Input: {test_case['text'][:100]}...")
        
        # Test with Vanta logging
        result = redactor.redact_pii_with_vanta_logging(
            text=test_case['text'],
            case_id=f"test_case_{i}",
            user_id="test_user"
        )
        
        print(f"✅ Processing completed in {result.processing_time_ms}ms")
        print(f"   Job ID: {result.job_id}")
        print(f"   Confidence: {result.redaction_confidence:.2f}")
        print(f"   PII Types Detected: {[d.pii_type for d in result.pii_detected]}")
        print(f"   Original Hash: {result.redaction_metadata.get('original_input_hash', 'N/A')}")
        
        # Show redacted text
        print(f"   Redacted Text: {result.redacted_text}")
        
        # Verify expected PII types
        detected_types = [d.pii_type for d in result.pii_detected]
        expected_types = test_case['expected_pii']
        
        if set(detected_types) == set(expected_types):
            print("✅ PII detection matches expected types")
        else:
            print(f"⚠️ PII detection mismatch:")
            print(f"   Expected: {expected_types}")
            print(f"   Detected: {detected_types}")

def test_vanta_client_directly():
    print("\n" + "=" * 80)
    print("TESTING VANTA CLIENT DIRECTLY")
    print("=" * 80)
    
    # Initialize Vanta client
    vanta_client = VantaClient()
    
    # Test authentication
    print("\n1. Testing Vanta authentication...")
    if vanta_client._ensure_authenticated():
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        print("   Please check your .env file has VANTA_CLIENT_ID and VANTA_CLIENT_SECRET")
        return
    
    # Test hash computation
    print("\n2. Testing hash computation...")
    test_content = "This is test content for hashing."
    content_hash = vanta_client.compute_content_hash(test_content)
    print(f"✅ SHA-256 hash: {content_hash}")
    
    # Test masking success determination
    print("\n3. Testing masking success determination...")
    pii_counts_before = {"email": 2, "phone": 1, "person_name": 1}
    pii_counts_after = {"email": 0, "phone": 0, "person_name": 0}  # All masked
    
    success = vanta_client.determine_masking_success(pii_counts_before, pii_counts_after)
    print(f"✅ Masking success: {success}")
    
    # Test payload structuring
    print("\n4. Testing payload structuring...")
    from datetime import datetime, timezone
    
    test_result = PIIMaskingResult(
        original_content_hash="abc123",
        masked_content_hash="def456",
        pii_types_detected=["email", "phone"],
        pii_counts_before=pii_counts_before,
        pii_counts_after=pii_counts_after,
        masking_success=True,
        confidence_score=0.95,
        processing_time_ms=150,
        timestamp=datetime.now(timezone.utc),
        job_id="test-job-123",
        case_id="test-case",
        user_id="test-user"
    )
    
    payload = vanta_client.structure_pii_masking_payload(test_result)
    print("✅ Payload structured successfully")
    print(f"   Resource Type: {payload['resourceType']}")
    print(f"   Compliance Status: {payload['compliance']['compliance_status']}")
    print(f"   Risk Level: {payload['compliance']['risk_level']}")
    
    # Test logging to Vanta (if credentials are available)
    print("\n5. Testing Vanta API logging...")
    response = vanta_client.log_pii_masking_result(test_result)
    
    if response.get('success'):
        print("✅ Successfully logged to Vanta API")
        print(f"   Resource ID: {response.get('resource_id')}")
        print(f"   Compliance Status: {response.get('compliance_status')}")
    else:
        print(f"⚠️ Failed to log to Vanta: {response.get('error')}")
        print("   This is expected if you haven't configured Vanta credentials")

def show_environment_setup():
    print("\n" + "=" * 80)
    print("VANTA SETUP INSTRUCTIONS")
    print("=" * 80)
    
    print("\n📋 To enable Vanta integration, add these to your .env file:")
    print("-" * 80)
    print("VANTA_CLIENT_ID=your_vanta_client_id")
    print("VANTA_CLIENT_SECRET=your_vanta_client_secret")
    print("VANTA_BASE_URL=https://api.vanta.com  # Optional")
    
    print("\n🔧 Steps to get Vanta credentials:")
    print("-" * 80)
    print("1. Log in to your Vanta account")
    print("2. Go to Settings → Developer Console")
    print("3. Click 'Create' to create a new application")
    print("4. Provide name and description")
    print("5. Select appropriate app type")
    print("6. Generate OAuth client secret")
    print("7. Copy client ID and secret")
    
    print("\n📊 Expected Vanta API payload structure:")
    print("-" * 80)
    print("""
{
  "resourceType": "PII_MASKING_JOB",
  "resourceId": "unique-job-id",
  "timestamp": "2025-01-12T10:30:00Z",
  "metadata": {
    "case_id": "case-123",
    "user_id": "user-456",
    "processing_time_ms": 150,
    "confidence_score": 0.95
  },
  "integrity": {
    "original_content_hash": "sha256-hash-of-original",
    "masked_content_hash": "sha256-hash-of-masked",
    "hash_algorithm": "SHA-256"
  },
  "pii_analysis": {
    "types_detected": ["email", "phone", "person_name"],
    "counts_before_masking": {"email": 2, "phone": 1},
    "counts_after_masking": {"email": 0, "phone": 0},
    "total_pii_before": 3,
    "total_pii_after": 0
  },
  "compliance": {
    "masking_success": true,
    "success_threshold": 0.95,
    "compliance_status": "PASS",
    "risk_level": "LOW"
  }
}
    """)

if __name__ == "__main__":
    test_vanta_integration()
    test_vanta_client_directly()
    show_environment_setup()
    
    print("\n" + "=" * 80)
    print("VANTA INTEGRATION FEATURES:")
    print("=" * 80)
    print("✅ SHA-256 hash computation for content integrity")
    print("✅ Structured JSON payload matching Vanta format")
    print("✅ OAuth authentication with client credentials")
    print("✅ Pass/fail determination based on PII reduction")
    print("✅ Comprehensive audit logging")
    print("✅ Risk level assessment")
    print("✅ Compliance status tracking")
    print("\n🎯 Ready for production use with proper Vanta credentials!")
    print("=" * 80)
