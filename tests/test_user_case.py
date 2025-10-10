#!/usr/bin/env python3
"""
Test user's specific case text
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from security.security_enforcer import SecurityEnforcer

# User's exact case text
case_text = """Case: Social Media Platform v. State Government

Facts: State law requires pre-approval of all online posts.
Company says this violates freedom of speech.

Legal Issues: 
1. Is prior censorship constitutional?
2. What are reasonable restrictions under Article 19(2)?
"""

print("=" * 80)
print("Testing User's Case Text")
print("=" * 80)
print("\nCase Text:")
print(case_text)
print("\n" + "=" * 80)
print("Security Analysis:")
print("=" * 80)

enforcer = SecurityEnforcer()

result = enforcer.process_case_input(
    case_text=case_text,
    user_id="test_user"
)

if result['success']:
    metadata = result['security_metadata']
    
    print(f"\n✅ Processing Successful")
    print(f"\n📊 Security Metadata:")
    print(f"   PII Types Detected: {metadata['pii_detected']}")
    print(f"   Number of Redactions: {metadata['num_redactions']}")
    print(f"   Risk Score: {metadata['risk_score']}")
    print(f"   Validation Passed: {metadata['validation_passed']}")
    
    if metadata['num_redactions'] > 0:
        print(f"\n⚠️  PII DETECTED (this seems wrong for this case):")
        print(f"   Redacted Text:")
        print(f"   {result['processed_text']}")
        print(f"\n   Let me analyze what was flagged as PII...")
    else:
        print(f"\n✅ No PII detected - this is correct!")
        print(f"   Processed text is identical to original")
else:
    print(f"\n❌ Processing failed: {result['error']}")
    print(f"   Violations: {result.get('violations', [])}")

print("\n" + "=" * 80)

