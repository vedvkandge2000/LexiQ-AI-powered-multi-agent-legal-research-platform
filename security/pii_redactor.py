#!/usr/bin/env python3
"""
PII Redactor Module
Detects and redacts Personally Identifiable Information while maintaining context.
Uses placeholders to preserve semantic meaning for LLM processing.
"""

import re
import hashlib
import uuid
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class PIIDetection:
    """Container for PII detection results."""
    pii_type: str
    original_value: str
    placeholder: str
    start_pos: int
    end_pos: int
    confidence: float


@dataclass
class PIIDetectionResult:
    """Result of PII detection and redaction."""
    original_text: str
    redacted_text: str
    pii_detected: List[PIIDetection]
    redaction_confidence: float
    redaction_metadata: Dict[str, Any]
    job_id: str = ""
    processing_time_ms: int = 0
    timestamp: datetime = None


class PIIRedactor:
    """
    Redacts PII from text while maintaining context using placeholders.
    
    Detects:
    - Person names (Indian and common international names)
    - Phone numbers (Indian and international formats)
    - Email addresses
    - Aadhaar numbers
    - PAN card numbers
    - Bank account numbers
    - Addresses (partial detection)
    """
    
    # Regex patterns for PII detection
    PATTERNS = {
        'phone': [
            r'\+?91[-\s]?\d{10}',  # Indian format: +91-9876543210
            r'\d{10}',  # 10-digit number
            r'\(\d{3}\)\s?\d{3}[-\s]?\d{4}',  # (123) 456-7890
        ],
        'email': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        'aadhaar': [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # 1234-5678-9012
            r'\b\d{12}\b',  # 123456789012
        ],
        'pan': [
            r'\b[A-Z]{5}\d{4}[A-Z]\b',  # ABCDE1234F
        ],
        'bank_account': [
            r'\b\d{9,18}\b',  # 9-18 digit account numbers
        ],
        'person_name': [
            # Indian name patterns (Title + Name)
            r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Justice|Hon\'?ble)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
            # Full name pattern (2-4 words, capitalized)
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
        ],
    }
    
    def __init__(self, enable_logging: bool = True):
        """
        Initialize PII Redactor.
        
        Args:
            enable_logging: Whether to enable detailed logging
        """
        self.enable_logging = enable_logging
        self.detection_cache = {}  # Cache for placeholder mappings
        
        # Initialize Vanta client if credentials are available
        self.vanta_client = None
        self.vanta_mcp_client = None
        
        # Try MCP client first (preferred)
        try:
            from integrations.vanta_mcp_client import create_vanta_mcp_client
            self.vanta_mcp_client = create_vanta_mcp_client()
            print("✅ Vanta MCP client initialized")
        except ImportError:
            print("⚠️ Vanta MCP integration not available")
        except Exception as e:
            print(f"⚠️ Vanta MCP client initialization failed: {e}")
        
        # Fallback to raw API client
        if not self.vanta_mcp_client:
            try:
                from integrations.vanta_client import create_vanta_client
                self.vanta_client = create_vanta_client()
                print("✅ Vanta raw API client initialized")
            except ImportError:
                print("⚠️ Vanta integration not available - install integrations module")
            except Exception as e:
                print(f"⚠️ Vanta client initialization failed: {e}")
        self.counter = {'phone': 0, 'email': 0, 'aadhaar': 0, 'pan': 0, 
                       'bank_account': 0, 'person_name': 0}
    
    def _generate_placeholder(self, pii_type: str, original_value: str) -> str:
        """
        Generate a consistent placeholder for PII.
        
        Args:
            pii_type: Type of PII (phone, email, etc.)
            original_value: Original PII value
            
        Returns:
            Placeholder string
        """
        # Use hash to ensure same value always gets same placeholder
        value_hash = hashlib.sha256(original_value.encode()).hexdigest()[:8]
        
        self.counter[pii_type] += 1
        count = self.counter[pii_type]
        
        placeholders = {
            'phone': f'[PHONE_{count}_{value_hash}]',
            'email': f'[EMAIL_{count}_{value_hash}]',
            'aadhaar': f'[AADHAAR_{count}_{value_hash}]',
            'pan': f'[PAN_{count}_{value_hash}]',
            'bank_account': f'[BANK_ACCOUNT_{count}_{value_hash}]',
            'person_name': f'[PERSON_{count}_{value_hash}]',
        }
        
        return placeholders.get(pii_type, f'[REDACTED_{pii_type.upper()}_{count}]')
    
    def _detect_pii(self, text: str) -> List[PIIDetection]:
        """
        Detect all PII in text.
        
        Args:
            text: Input text
            
        Returns:
            List of PIIDetection objects
        """
        detections = []
        
        for pii_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    original_value = match.group(0)
                    
                    # Skip if likely not PII (context-based filtering)
                    if self._is_false_positive(pii_type, original_value, text, match.start()):
                        continue
                    
                    placeholder = self._generate_placeholder(pii_type, original_value)
                    
                    detection = PIIDetection(
                        pii_type=pii_type,
                        original_value=original_value,
                        placeholder=placeholder,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=self._calculate_confidence(pii_type, original_value, text)
                    )
                    detections.append(detection)
        
        # Sort by position (reverse order for replacement)
        detections.sort(key=lambda x: x.start_pos, reverse=True)
        
        return detections
    
    def _is_false_positive(self, pii_type: str, value: str, text: str, position: int) -> bool:
        """
        Check if detected PII is likely a false positive.
        
        Args:
            pii_type: Type of PII
            value: Detected value
            text: Full text
            position: Position in text
            
        Returns:
            True if likely false positive
        """
        # Context-based filtering
        context_start = max(0, position - 50)
        context_end = min(len(text), position + len(value) + 50)
        context = text[context_start:context_end].lower()
        
        if pii_type == 'person_name':
            # Skip common legal terms, entities, and section headers
            skip_terms = [
                # Legal terms
                'supreme court', 'high court', 'civil appeal', 'criminal appeal',
                'state of', 'union of', 'petitioner', 'respondent', 'appellant',
                # Government entities
                'state government', 'central government', 'union government',
                'government of', 'ministry of',
                # Common legal entities
                'company', 'corporation', 'platform', 'limited', 'ltd',
                'private limited', 'pvt ltd', 'public limited',
                # Section headers
                'legal issues', 'facts', 'arguments', 'case:', 'v.', 'vs.',
                'background', 'issues', 'judgment', 'order', 'relief',
                # Generic entities
                'social media', 'bank', 'insurance', 'trust', 'society',
            ]
            
            value_lower = value.lower()
            
            # Check if value itself is a skip term
            if any(term in value_lower for term in skip_terms):
                return True
            
            # Check context
            if any(term in context for term in skip_terms):
                # But allow if preceded by "Justice", "Mr.", etc.
                if not any(title in context for title in ['justice', 'mr.', 'mrs.', 'ms.', 'dr.']):
                    return True
            
            # Skip if it's all caps (likely an acronym or case name)
            if value.isupper() and len(value) > 2:
                return True
        
        elif pii_type == 'phone':
            # Skip if it's a case number or section number
            if 'section' in context or 'case no' in context or 'appeal no' in context:
                return True
        
        elif pii_type == 'bank_account':
            # Skip if it's a year, case number, or section
            if re.match(r'\b(19|20)\d{2}\b', value):  # Year
                return True
            if 'section' in context or 'case' in context:
                return True
        
        return False
    
    def _calculate_confidence(self, pii_type: str, value: str, text: str) -> float:
        """
        Calculate confidence score for PII detection.
        
        Args:
            pii_type: Type of PII
            value: Detected value
            text: Full text
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = {
            'email': 0.95,  # Email regex is very reliable
            'aadhaar': 0.90,  # Specific format
            'pan': 0.95,  # Very specific format
            'phone': 0.75,  # Can be confused with other numbers
            'bank_account': 0.60,  # Often confused with case numbers
            'person_name': 0.70,  # Name detection is tricky
        }
        
        confidence = base_confidence.get(pii_type, 0.5)
        
        # Adjust based on context
        # (You can add more sophisticated confidence calculation here)
        
        return confidence
    
    def redact(self, text: str, min_confidence: float = 0.7) -> Dict[str, Any]:
        """
        Redact PII from text while maintaining context.
        
        Args:
            text: Input text
            min_confidence: Minimum confidence threshold for redaction
            
        Returns:
            Dictionary with redacted text and metadata
        """
        # Reset counters for each redaction
        self.counter = {k: 0 for k in self.counter.keys()}
        
        # Detect PII
        detections = self._detect_pii(text)
        
        # Filter by confidence
        detections = [d for d in detections if d.confidence >= min_confidence]
        
        # Replace PII with placeholders
        redacted_text = text
        placeholder_map = {}
        
        for detection in detections:
            # Replace in text (already sorted in reverse order)
            redacted_text = (
                redacted_text[:detection.start_pos] + 
                detection.placeholder + 
                redacted_text[detection.end_pos:]
            )
            
            # Store mapping
            placeholder_map[detection.placeholder] = {
                'original_value_hash': hashlib.sha256(detection.original_value.encode()).hexdigest(),
                'pii_type': detection.pii_type,
                'confidence': detection.confidence
            }
        
        # Generate original input hash
        original_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Prepare PII types detected
        pii_types = list(set([d.pii_type for d in detections]))
        
        # Calculate overall confidence
        avg_confidence = sum(d.confidence for d in detections) / len(detections) if detections else 1.0
        
        return {
            'redacted_text': redacted_text,
            'original_input_hash': original_hash,
            'pii_types_detected': pii_types,
            'num_redactions': len(detections),
            'placeholder_map': placeholder_map,
            'redaction_confidence_score': round(avg_confidence, 3),
            'redaction_details': [
                {
                    'type': d.pii_type,
                    'placeholder': d.placeholder,
                    'confidence': round(d.confidence, 3)
                }
                for d in detections
            ]
        }
    
    def unredact(self, redacted_text: str, placeholder_map: Dict[str, Dict]) -> str:
        """
        Restore original values from placeholders (use with caution).
        
        Args:
            redacted_text: Text with placeholders
            placeholder_map: Mapping of placeholders to original values
            
        Returns:
            Text with restored values
        """
        # This method should only be used in secure contexts
        # In production, you may want to disable this or add additional auth
        raise NotImplementedError("Unredaction disabled for security")
    
    def redact_pii_with_vanta_logging(self, 
                                    text: str, 
                                    case_id: str = None, 
                                    user_id: str = None) -> PIIDetectionResult:
        """
        Detect and redact PII with Vanta compliance logging.
        
        Args:
            text: Input text to process
            case_id: Optional case identifier for tracking
            user_id: Optional user identifier for tracking
            
        Returns:
            PIIDetectionResult with redacted text and metadata
        """
        start_time = time.time()
        job_id = str(uuid.uuid4())
        
        # Detect and redact PII using existing method
        redaction_metadata = self.redact(text)
        redacted_text = redaction_metadata.get('redacted_text', text)
        
        # Convert to PIIDetection objects
        pii_detected = []
        for pii_type in redaction_metadata.get('pii_types_detected', []):
            pii_detected.append(PIIDetection(
                pii_type=pii_type,
                original_value='',  # Not stored in original format
                placeholder=f'[{pii_type.upper()}_REDACTED]',
                start_pos=0,
                end_pos=0,
                confidence=redaction_metadata.get('redaction_confidence_score', 0.9)
            ))
        
        processing_time = int((time.time() - start_time) * 1000)
        
        result = PIIDetectionResult(
            original_text=text,
            redacted_text=redacted_text,
            pii_detected=pii_detected,
            redaction_confidence=redaction_metadata.get('redaction_confidence_score', 0.9),
            redaction_metadata=redaction_metadata,
            job_id=job_id,
            processing_time_ms=processing_time,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Log to Vanta if client is available
        self._log_to_vanta(result, case_id, user_id)
        
        return result
    
    def _log_to_vanta(self, result: PIIDetectionResult, case_id: str = None, user_id: str = None):
        """Log PII masking result to Vanta."""
        if not self.vanta_client:
            return
        
        try:
            # Count PII types before and after
            pii_counts_before = {}
            pii_counts_after = {}
            pii_types_detected = result.redaction_metadata.get('pii_types_detected', [])
            
            # Count before masking (from detected PII)
            num_redactions = result.redaction_metadata.get('num_redactions', 0)
            for pii_type in pii_types_detected:
                pii_counts_before[pii_type] = 1  # Simplified count
                pii_counts_after[pii_type] = 0  # All should be masked
            
            # Determine masking success
            masking_success = self.vanta_client.determine_masking_success(
                pii_counts_before, pii_counts_after
            )
            
            # Create PIIMaskingResult for Vanta
            from integrations.vanta_client import PIIMaskingResult
            
            vanta_result = PIIMaskingResult(
                original_content_hash=self.vanta_client.compute_content_hash(result.original_text),
                masked_content_hash=self.vanta_client.compute_content_hash(result.redacted_text),
                pii_types_detected=pii_types_detected,
                pii_counts_before=pii_counts_before,
                pii_counts_after=pii_counts_after,
                masking_success=masking_success,
                confidence_score=result.redaction_confidence,
                processing_time_ms=result.processing_time_ms,
                timestamp=result.timestamp,
                job_id=result.job_id,
                case_id=case_id,
                user_id=user_id
            )
            
            # Log to Vanta
            vanta_response = self.vanta_client.log_pii_masking_result(vanta_result)
            
            if vanta_response.get('success'):
                print(f"✅ PII masking logged to Vanta: {result.job_id}")
                print(f"   Compliance Status: {vanta_response.get('compliance_status')}")
            else:
                print(f"⚠️ Failed to log to Vanta: {vanta_response.get('error')}")
                
        except Exception as e:
            print(f"❌ Error logging to Vanta: {e}")
    
    def redact_pii_with_vanta_mcp_logging(self, 
                                        text: str, 
                                        case_id: str = None, 
                                        user_id: str = None) -> PIIDetectionResult:
        """
        Detect and redact PII with Vanta MCP compliance logging.
        
        Args:
            text: Input text to process
            case_id: Optional case identifier for tracking
            user_id: Optional user identifier for tracking
            
        Returns:
            PIIDetectionResult with redacted text and metadata
        """
        start_time = time.time()
        job_id = str(uuid.uuid4())
        
        # Detect and redact PII using existing method
        redaction_metadata = self.redact(text)
        redacted_text = redaction_metadata.get('redacted_text', text)
        
        # Convert to PIIDetection objects
        pii_detected = []
        for pii_type in redaction_metadata.get('pii_types_detected', []):
            pii_detected.append(PIIDetection(
                pii_type=pii_type,
                original_value='',  # Not stored in original format
                placeholder=f'[{pii_type.upper()}_REDACTED]',
                start_pos=0,
                end_pos=0,
                confidence=redaction_metadata.get('redaction_confidence_score', 0.9)
            ))
        
        processing_time = int((time.time() - start_time) * 1000)
        
        result = PIIDetectionResult(
            original_text=text,
            redacted_text=redacted_text,
            pii_detected=pii_detected,
            redaction_confidence=redaction_metadata.get('redaction_confidence_score', 0.9),
            redaction_metadata=redaction_metadata,
            job_id=job_id,
            processing_time_ms=processing_time,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Log to Vanta MCP if client is available
        self._log_to_vanta_mcp(result, case_id, user_id)
        
        # Log to local audit trail
        self._log_to_audit_trail(result, case_id, user_id)
        
        return result
    
    def _log_to_vanta_mcp(self, result: PIIDetectionResult, case_id: str = None, user_id: str = None):
        """Log PII masking result to Vanta via MCP server."""
        if not self.vanta_mcp_client:
            print("⚠️ Vanta MCP client not available")
            return
        
        try:
            # Count PII types before and after
            pii_counts_before = {}
            pii_counts_after = {}
            pii_types_detected = result.redaction_metadata.get('pii_types_detected', [])
            
            # Count before masking (from detected PII)
            num_redactions = result.redaction_metadata.get('num_redactions', 0)
            for pii_type in pii_types_detected:
                pii_counts_before[pii_type] = 1  # Simplified count
                pii_counts_after[pii_type] = 0  # All should be masked
            
            # Determine masking success
            masking_success = self.vanta_mcp_client.determine_masking_success(
                pii_counts_before, pii_counts_after
            )
            
            # Create PIIMaskingResult for Vanta MCP
            from integrations.vanta_mcp_client import PIIMaskingResult
            
            vanta_result = PIIMaskingResult(
                original_content_hash=self.vanta_mcp_client.compute_content_hash(result.original_text),
                masked_content_hash=self.vanta_mcp_client.compute_content_hash(result.redacted_text),
                pii_types_detected=pii_types_detected,
                pii_counts_before=pii_counts_before,
                pii_counts_after=pii_counts_after,
                masking_success=masking_success,
                confidence_score=result.redaction_confidence,
                processing_time_ms=result.processing_time_ms,
                timestamp=result.timestamp,
                job_id=result.job_id,
                case_id=case_id,
                user_id=user_id
            )
            
            # Log to Vanta MCP
            vanta_response = self.vanta_mcp_client.log_pii_masking_result(vanta_result)
            
            if vanta_response.get('success'):
                print(f"✅ PII masking logged to Vanta MCP: {result.job_id}")
                print(f"   Compliance Status: {vanta_response.get('compliance_status')}")
                print(f"   MCP Integration: {vanta_response.get('mcp_integration')}")
            else:
                print(f"⚠️ Failed to log to Vanta MCP: {vanta_response.get('error')}")
                
        except Exception as e:
            print(f"❌ Error logging to Vanta MCP: {e}")
    
    def _log_to_audit_trail(self, result: PIIDetectionResult, case_id: str = None, user_id: str = None):
        """Log PII masking result to local audit trail."""
        try:
            import os
            import json
            
            # Ensure logs directory exists
            os.makedirs('security/logs', exist_ok=True)
            
            # Count PII types before and after
            pii_counts_before = {}
            pii_counts_after = {}
            pii_types_detected = result.redaction_metadata.get('pii_types_detected', [])
            
            num_redactions = result.redaction_metadata.get('num_redactions', 0)
            for pii_type in pii_types_detected:
                pii_counts_before[pii_type] = 1  # Simplified count
                pii_counts_after[pii_type] = 0  # All should be masked
            
            # Determine compliance status
            compliance_status = "PASS" if result.redaction_confidence > 0.8 else "REVIEW"
            
            # Determine risk level
            total_remaining = sum(pii_counts_after.values())
            if total_remaining == 0:
                risk_level = "LOW"
            elif total_remaining <= 2:
                risk_level = "MEDIUM"
            elif total_remaining <= 5:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"
            
            # Create audit entry
            audit_entry = {
                'timestamp': result.timestamp.isoformat(),
                'event_type': 'PII_MASKING_JOB',
                'job_id': result.job_id,
                'case_id': case_id,
                'user_id': user_id,
                'compliance_status': compliance_status,
                'risk_level': risk_level,
                'pii_types_detected': pii_types_detected,
                'pii_counts_before': pii_counts_before,
                'pii_counts_after': pii_counts_after,
                'masking_success': result.redaction_confidence > 0.8,
                'confidence_score': result.redaction_confidence,
                'original_content_hash': result.redaction_metadata.get('original_input_hash', ''),
                'masked_content_hash': result.redaction_metadata.get('redacted_input_hash', ''),
                'vanta_logged': self.vanta_mcp_client is not None,
                'processing_time_ms': result.processing_time_ms
            }
            
            # Append to PII audit log
            log_file = 'security/logs/pii_audit.log'
            with open(log_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
            
            print(f"📝 PII audit entry logged: {result.job_id}")
                
        except Exception as e:
            print(f"❌ Error logging to audit trail: {e}")

