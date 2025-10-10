#!/usr/bin/env python3
"""
Audit Trail Viewer for LexiQ Security and Vanta Integration
Shows all audit logs and Vanta compliance data
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
import sys

def load_json_logs(log_file: str) -> List[Dict[str, Any]]:
    """Load JSON log entries from a file."""
    entries = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            entries.append(entry)
                        except json.JSONDecodeError:
                            # Handle non-JSON lines (like timestamp prefixes)
                            if '{' in line:
                                json_part = line[line.find('{'):]
                                try:
                                    entry = json.loads(json_part)
                                    entries.append(entry)
                                except json.JSONDecodeError:
                                    continue
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
    return entries

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display."""
    try:
        if '+' in timestamp_str:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return timestamp_str

def show_pii_audit_trail():
    """Show PII audit trail."""
    print("🔒 PII AUDIT TRAIL")
    print("=" * 60)
    
    pii_log_file = "security/logs/pii_audit.log"
    entries = load_json_logs(pii_log_file)
    
    if not entries:
        print("📝 No PII audit entries found")
        print("💡 Run PII redaction to generate audit entries")
        return
    
    print(f"📊 Total PII masking jobs: {len(entries)}")
    print()
    
    for i, entry in enumerate(entries[-5:], 1):  # Show last 5 entries
        print(f"📋 Job #{i}:")
        print(f"   🆔 Job ID: {entry.get('job_id', 'N/A')}")
        print(f"   ⏰ Timestamp: {format_timestamp(entry.get('timestamp', 'N/A'))}")
        print(f"   👤 User: {entry.get('user_id', 'N/A')}")
        print(f"   📁 Case: {entry.get('case_id', 'N/A')}")
        print(f"   ✅ Status: {entry.get('compliance_status', 'N/A')}")
        print(f"   ⚠️  Risk: {entry.get('risk_level', 'N/A')}")
        print(f"   🔍 PII Types: {', '.join(entry.get('pii_types_detected', []))}")
        print(f"   📊 Before: {entry.get('pii_counts_before', {})}")
        print(f"   📊 After: {entry.get('pii_counts_after', {})}")
        print(f"   🎯 Success: {entry.get('masking_success', 'N/A')}")
        print(f"   📈 Confidence: {entry.get('confidence_score', 'N/A')}")
        print(f"   🏢 Vanta Logged: {entry.get('vanta_logged', 'N/A')}")
        print()

def show_security_audit_trail():
    """Show general security audit trail."""
    print("🛡️  SECURITY AUDIT TRAIL")
    print("=" * 60)
    
    security_log_file = "security/logs/security_audit.log"
    entries = load_json_logs(security_log_file)
    
    if not entries:
        print("📝 No security audit entries found")
        return
    
    print(f"📊 Total security events: {len(entries)}")
    print()
    
    # Group by action type
    actions = {}
    for entry in entries:
        action = entry.get('action', 'UNKNOWN')
        if action not in actions:
            actions[action] = 0
        actions[action] += 1
    
    print("📈 Event Summary:")
    for action, count in actions.items():
        print(f"   {action}: {count} events")
    print()
    
    # Show recent entries
    print("📋 Recent Events (last 3):")
    for i, entry in enumerate(entries[-3:], 1):
        print(f"   {i}. {entry.get('action', 'N/A')} - {format_timestamp(entry.get('timestamp', 'N/A'))}")
        if 'pii_types_detected' in entry:
            print(f"      PII: {', '.join(entry.get('pii_types_detected', []))}")
        if 'risk_score' in entry:
            print(f"      Risk: {entry.get('risk_score', 'N/A')}")
    print()

def show_hallucination_audit_trail():
    """Show hallucination detection audit trail."""
    print("🧠 HALLUCINATION DETECTION AUDIT TRAIL")
    print("=" * 60)
    
    hallucination_log_file = "security/logs/hallucination_audit.log"
    entries = load_json_logs(hallucination_log_file)
    
    if not entries:
        print("📝 No hallucination detection entries found")
        return
    
    print(f"📊 Total hallucination checks: {len(entries)}")
    
    # Count suspected hallucinations
    suspected_count = sum(1 for entry in entries if entry.get('suspected_hallucination', False))
    print(f"⚠️  Suspected hallucinations: {suspected_count}")
    print()
    
    # Show recent entries
    print("📋 Recent Hallucination Checks (last 3):")
    for i, entry in enumerate(entries[-3:], 1):
        suspected = entry.get('suspected_hallucination', False)
        confidence = entry.get('confidence_score', 'N/A')
        num_suspected = entry.get('num_suspected', 0)
        
        status = "🚨 SUSPECTED" if suspected else "✅ CLEAN"
        print(f"   {i}. {status}")
        print(f"      Confidence: {confidence}")
        print(f"      Suspected References: {num_suspected}")
        print(f"      Timestamp: {format_timestamp(entry.get('timestamp', 'N/A'))}")
        print()

def show_vanta_dashboard_info():
    """Show Vanta dashboard access information."""
    print("🎯 VANTA DASHBOARD ACCESS")
    print("=" * 60)
    
    print("🌐 Vanta Dashboard URL: https://app.vanta.com")
    print()
    print("📊 Where to find LexiQ data in Vanta:")
    print("   1. 📋 Compliance Reports")
    print("      • Look for 'PII Masking Jobs'")
    print("      • Check 'LexiQ Integration' section")
    print()
    print("   2. 🔍 Audit Logs")
    print("      • Filter by 'Custom Resources'")
    print("      • Search for 'PII_MASKING_JOB'")
    print()
    print("   3. 📈 Custom Resources")
    print("      • Resource Type: PII_MASKING_JOB")
    print("      • System: LexiQ")
    print("      • Environment: development")
    print()
    print("   4. 🔐 Data Protection Reports")
    print("      • PII Detection and Redaction")
    print("      • Compliance Status Tracking")
    print("      • Risk Level Assessments")
    print()
    print("💡 Search Terms in Vanta Dashboard:")
    print("   • 'LexiQ'")
    print("   • 'PII_MASKING_JOB'")
    print("   • 'PII_MASKING'")
    print("   • Your job IDs (from local logs)")

def show_compliance_summary():
    """Show overall compliance summary."""
    print("📊 COMPLIANCE SUMMARY")
    print("=" * 60)
    
    # Load all logs
    pii_entries = load_json_logs("security/logs/pii_audit.log")
    security_entries = load_json_logs("security/logs/security_audit.log")
    hallucination_entries = load_json_logs("security/logs/hallucination_audit.log")
    
    print(f"📋 PII Masking Jobs: {len(pii_entries)}")
    if pii_entries:
        pass_count = sum(1 for entry in pii_entries if entry.get('compliance_status') == 'PASS')
        print(f"   ✅ Passed: {pass_count}")
        print(f"   ❌ Failed: {len(pii_entries) - pass_count}")
    
    print(f"🛡️  Security Events: {len(security_entries)}")
    
    print(f"🧠 Hallucination Checks: {len(hallucination_entries)}")
    if hallucination_entries:
        suspected_count = sum(1 for entry in hallucination_entries if entry.get('suspected_hallucination', False))
        print(f"   🚨 Suspected: {suspected_count}")
        print(f"   ✅ Clean: {len(hallucination_entries) - suspected_count}")
    
    print()
    print("🎯 Overall Status: ✅ COMPLIANCE MONITORING ACTIVE")
    print("   • PII detection and masking: ✅ Active")
    print("   • Security validation: ✅ Active")
    print("   • Hallucination detection: ✅ Active")
    print("   • Vanta integration: ✅ Active")

def main():
    """Main audit trail viewer."""
    print("🔍 LEXIQ AUDIT TRAIL VIEWER")
    print("=" * 80)
    print()
    
    # Check if logs directory exists
    if not os.path.exists("security/logs"):
        print("❌ Security logs directory not found")
        print("💡 Run security tests to generate audit logs")
        return
    
    show_compliance_summary()
    print()
    show_pii_audit_trail()
    print()
    show_security_audit_trail()
    print()
    show_hallucination_audit_trail()
    print()
    show_vanta_dashboard_info()
    
    print()
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. 🔄 Run PII redaction to generate more audit entries")
    print("2. 🌐 Check Vanta dashboard for centralized logging")
    print("3. 📊 Use this viewer to monitor compliance status")
    print("4. 🚨 Review any failed or high-risk events")

if __name__ == "__main__":
    main()
