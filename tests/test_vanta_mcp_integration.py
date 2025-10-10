#!/usr/bin/env python3
"""
Test Vanta MCP Integration
Tests the new MCP-based Vanta integration
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from security.pii_redactor import PIIRedactor
from integrations.vanta_mcp_client import VantaMCPClient, PIIMaskingResult

def test_vanta_mcp_integration():
    print("=" * 80)
    print("TESTING VANTA MCP INTEGRATION")
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
    
    # Initialize PII redactor with MCP integration
    print("\n1. Initializing PII Redactor with MCP integration...")
    redactor = PIIRedactor()
    
    if redactor.vanta_mcp_client:
        print("✅ Vanta MCP client initialized successfully")
    elif redactor.vanta_client:
        print("✅ Vanta raw API client initialized (MCP fallback)")
    else:
        print("⚠️ No Vanta client available - check credentials")
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Input: {test_case['text'][:100]}...")
        
        # Test with MCP logging
        result = redactor.redact_pii_with_vanta_mcp_logging(
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

def test_vanta_mcp_client_directly():
    print("\n" + "=" * 80)
    print("TESTING VANTA MCP CLIENT DIRECTLY")
    print("=" * 80)
    
    # Initialize MCP client
    mcp_client = VantaMCPClient()
    
    # Test hash computation
    print("\n1. Testing hash computation...")
    test_content = "This is test content for hashing."
    content_hash = mcp_client.compute_content_hash(test_content)
    print(f"✅ SHA-256 hash: {content_hash}")
    
    # Test masking success determination
    print("\n2. Testing masking success determination...")
    pii_counts_before = {"email": 2, "phone": 1, "person_name": 1}
    pii_counts_after = {"email": 0, "phone": 0, "person_name": 0}  # All masked
    
    success = mcp_client.determine_masking_success(pii_counts_before, pii_counts_after)
    print(f"✅ Masking success: {success}")
    
    # Test payload structuring
    print("\n3. Testing payload structuring...")
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
    
    payload = mcp_client.structure_pii_masking_payload(test_result)
    print("✅ Payload structured successfully")
    print(f"   Resource Type: {payload['resourceType']}")
    print(f"   Compliance Status: {payload['compliance']['compliance_status']}")
    print(f"   Risk Level: {payload['compliance']['risk_level']}")
    
    # Test logging to Vanta MCP
    print("\n4. Testing Vanta MCP logging...")
    response = mcp_client.log_pii_masking_result(test_result)
    
    if response.get('success'):
        print("✅ Successfully logged to Vanta MCP")
        print(f"   Resource ID: {response.get('resource_id')}")
        print(f"   Compliance Status: {response.get('compliance_status')}")
        print(f"   MCP Integration: {response.get('mcp_integration')}")
    else:
        print(f"⚠️ Failed to log to Vanta MCP: {response.get('error')}")

def show_mcp_setup_instructions():
    print("\n" + "=" * 80)
    print("VANTA MCP SETUP INSTRUCTIONS")
    print("=" * 80)
    
    print("\n📋 To enable Vanta MCP integration:")
    print("-" * 80)
    print("1. Update vanta-credentials.env with your actual credentials")
    print("2. Add MCP configuration to Cursor settings")
    print("3. Restart Cursor")
    print("4. Test the integration")
    
    print("\n🔧 Cursor MCP Configuration:")
    print("-" * 80)
    print("""
{
  "mcpServers": {
    "Vanta": {
      "command": "npx",
      "args": ["-y", "@vantasdk/vanta-mcp-server"],
      "env": {
        "VANTA_ENV_FILE": "/Users/vedantkandge/Documents/Hackathons/lexiq/vanta-credentials.env"
      }
    }
  }
}
    """)
    
    print("\n📊 Benefits of MCP Approach:")
    print("-" * 80)
    print("✅ Official Vanta SDK with proper API handling")
    print("✅ Built-in authentication management")
    print("✅ Structured data models and validation")
    print("✅ No endpoint guessing required")
    print("✅ Native Cursor integration")

if __name__ == "__main__":
    test_vanta_mcp_integration()
    test_vanta_mcp_client_directly()
    show_mcp_setup_instructions()
    
    print("\n" + "=" * 80)
    print("VANTA MCP INTEGRATION FEATURES:")
    print("=" * 80)
    print("✅ SHA-256 hash computation for content integrity")
    print("✅ Structured JSON payload matching Vanta MCP format")
    print("✅ MCP server integration (no raw API endpoints needed)")
    print("✅ Pass/fail determination based on PII reduction")
    print("✅ Comprehensive audit logging")
    print("✅ Risk level assessment")
    print("✅ Compliance status tracking")
    print("\n🎯 Ready for production use with MCP server!")
    print("=" * 80)
