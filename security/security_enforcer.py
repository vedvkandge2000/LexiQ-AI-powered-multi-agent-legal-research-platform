#!/usr/bin/env python3
"""
Security Enforcer Module
Backend enforcement layer that all requests must pass through.
Combines input validation, PII redaction, and security logging.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from .pii_redactor import PIIRedactor
from .input_validator import InputValidator


@dataclass
class SecurityLog:
    """Container for security audit logs."""
    timestamp: str
    request_id: str
    user_id: Optional[str]
    action: str
    original_input_hash: str
    pii_types_detected: list
    num_redactions: int
    redaction_confidence_score: float
    validation_passed: bool
    risk_score: float
    violations: list
    ip_address: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class SecurityEnforcer:
    """
    Backend security enforcement module.
    All requests must pass through this layer before processing.
    """
    
    def __init__(self, 
                 enable_pii_redaction: bool = True,
                 enable_validation: bool = True,
                 min_pii_confidence: float = 0.7,
                 log_file: str = "security/logs/security_audit.log"):
        """
        Initialize Security Enforcer.
        
        Args:
            enable_pii_redaction: Whether to enable PII redaction
            enable_validation: Whether to enable input validation
            min_pii_confidence: Minimum confidence for PII redaction
            log_file: Path to security audit log file
        """
        self.enable_pii_redaction = enable_pii_redaction
        self.enable_validation = enable_validation
        self.min_pii_confidence = min_pii_confidence
        
        # Initialize components
        self.pii_redactor = PIIRedactor() if enable_pii_redaction else None
        self.input_validator = InputValidator() if enable_validation else None
        
        # Setup logging
        self._setup_logging(log_file)
        
        # Request counter for IDs
        self.request_counter = 0
    
    def _setup_logging(self, log_file: str):
        """Setup security audit logging."""
        # Create logger
        self.logger = logging.getLogger('LexiQ.Security')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        try:
            import os
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup security logging: {e}")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        self.request_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"REQ_{timestamp}_{self.request_counter:06d}"
    
    def process_case_input(self, 
                          case_text: str,
                          user_id: Optional[str] = None,
                          ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Process case input through security enforcement.
        
        Args:
            case_text: User's case description
            user_id: Optional user identifier
            ip_address: Optional IP address
            
        Returns:
            Dictionary with processed text and security metadata
        """
        request_id = self._generate_request_id()
        
        # Step 1: Input Validation
        validation_result = None
        if self.enable_validation:
            validation_result = self.input_validator.validate_case_text(case_text)
            
            if not validation_result.is_valid:
                # Log violation
                self._log_security_event(
                    request_id=request_id,
                    user_id=user_id,
                    ip_address=ip_address,
                    action="INPUT_VALIDATION_FAILED",
                    original_input_hash=None,
                    pii_data={},
                    validation_result=validation_result
                )
                
                return {
                    'success': False,
                    'error': 'Input validation failed',
                    'violations': validation_result.violations,
                    'risk_score': validation_result.risk_score,
                    'request_id': request_id
                }
            
            # Use sanitized input
            case_text = validation_result.sanitized_input
        
        # Step 2: PII Redaction
        redaction_result = None
        processed_text = case_text
        
        if self.enable_pii_redaction:
            redaction_result = self.pii_redactor.redact(
                case_text, 
                min_confidence=self.min_pii_confidence
            )
            processed_text = redaction_result['redacted_text']
        
        # Step 3: Log successful processing
        self._log_security_event(
            request_id=request_id,
            user_id=user_id,
            ip_address=ip_address,
            action="CASE_INPUT_PROCESSED",
            original_input_hash=redaction_result['original_input_hash'] if redaction_result else None,
            pii_data=redaction_result or {},
            validation_result=validation_result
        )
        
        # Return processed data
        return {
            'success': True,
            'processed_text': processed_text,
            'original_length': len(case_text),
            'processed_length': len(processed_text),
            'request_id': request_id,
            'security_metadata': {
                'validation_passed': validation_result.is_valid if validation_result else True,
                'risk_score': validation_result.risk_score if validation_result else 0.0,
                'pii_detected': redaction_result['pii_types_detected'] if redaction_result else [],
                'num_redactions': redaction_result['num_redactions'] if redaction_result else 0,
                'redaction_confidence': redaction_result['redaction_confidence_score'] if redaction_result else 1.0,
                'original_input_hash': redaction_result['original_input_hash'] if redaction_result else None,
                'placeholder_map': redaction_result.get('placeholder_map', {}) if redaction_result else {}
            }
        }
    
    def process_file_upload(self,
                           filename: str,
                           file_size_bytes: int,
                           content_type: str,
                           user_id: Optional[str] = None,
                           ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Process file upload through security enforcement.
        
        Args:
            filename: Name of uploaded file
            file_size_bytes: File size in bytes
            content_type: MIME type
            user_id: Optional user identifier
            ip_address: Optional IP address
            
        Returns:
            Dictionary with validation result
        """
        request_id = self._generate_request_id()
        
        if not self.enable_validation:
            return {'success': True, 'request_id': request_id}
        
        # Validate file upload
        validation_result = self.input_validator.validate_file_upload(
            filename, file_size_bytes, content_type
        )
        
        # Log
        self._log_security_event(
            request_id=request_id,
            user_id=user_id,
            ip_address=ip_address,
            action="FILE_UPLOAD_VALIDATION",
            original_input_hash=None,
            pii_data={'filename': validation_result.sanitized_input},
            validation_result=validation_result
        )
        
        if not validation_result.is_valid:
            return {
                'success': False,
                'error': 'File validation failed',
                'violations': validation_result.violations,
                'risk_score': validation_result.risk_score,
                'request_id': request_id
            }
        
        return {
            'success': True,
            'sanitized_filename': validation_result.sanitized_input,
            'request_id': request_id
        }
    
    def _log_security_event(self,
                           request_id: str,
                           user_id: Optional[str],
                           ip_address: Optional[str],
                           action: str,
                           original_input_hash: Optional[str],
                           pii_data: Dict,
                           validation_result: Any):
        """
        Log security event to audit log.
        
        Args:
            request_id: Request identifier
            user_id: User identifier
            ip_address: IP address
            action: Action performed
            original_input_hash: Hash of original input
            pii_data: PII redaction data
            validation_result: Validation result
        """
        log_entry = SecurityLog(
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            user_id=user_id,
            action=action,
            original_input_hash=original_input_hash or "N/A",
            pii_types_detected=pii_data.get('pii_types_detected', []),
            num_redactions=pii_data.get('num_redactions', 0),
            redaction_confidence_score=pii_data.get('redaction_confidence_score', 1.0),
            validation_passed=validation_result.is_valid if validation_result else True,
            risk_score=validation_result.risk_score if validation_result else 0.0,
            violations=validation_result.violations if validation_result else [],
            ip_address=ip_address
        )
        
        # Log to file
        self.logger.info(json.dumps(log_entry.to_dict()))
    
    def get_security_stats(self) -> Dict[str, Any]:
        """
        Get security statistics.
        
        Returns:
            Dictionary with security stats
        """
        return {
            'total_requests': self.request_counter,
            'pii_redaction_enabled': self.enable_pii_redaction,
            'validation_enabled': self.enable_validation,
            'min_pii_confidence': self.min_pii_confidence
        }

