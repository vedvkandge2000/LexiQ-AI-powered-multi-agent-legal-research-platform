#!/usr/bin/env python3
"""
Input Validator Module
Validates and sanitizes all user inputs before processing.
"""

import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Container for validation results."""
    is_valid: bool
    sanitized_input: str
    violations: List[str]
    risk_score: float


class InputValidator:
    """
    Validates and sanitizes user inputs.
    
    Checks for:
    - Length limits
    - Malicious patterns
    - Prompt injection attempts
    - XSS attempts
    - SQL injection patterns (defensive)
    - Excessive special characters
    """
    
    # Configuration
    MAX_TEXT_LENGTH = 50000  # Max characters for case text
    MAX_FILE_SIZE_MB = 10
    MIN_TEXT_LENGTH = 10
    
    # Suspicious patterns
    PROMPT_INJECTION_PATTERNS = [
        r'ignore\s+(?:all\s+)?(?:previous|above|prior|the\s+above)\s+(?:instructions?|commands?)',
        r'disregard\s+(?:previous|above|prior)',
        r'forget\s+(?:previous|above|prior)',
        r'you\s+are\s+now\s+(?:in\s+)?(?:admin|system|root)',
        r'new\s+instructions?:',
        r'system\s*:\s*(?:ignore|disregard|forget)',
        r'system\s+(?:prompt|mode):',
        r'jailbreak',
        r'DAN\s+mode',
        r'(?:begin|start|end)\s+(?:system|admin)',
        r'\[system\]',
        r'/\*\s*system\s*\*/',
        r'override\s+(?:security|protocols)',
        r'instructions?\s+(?:are\s+)?void',
    ]
    
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'<iframe',
        r'<embed',
        r'<object',
    ]
    
    SQL_PATTERNS = [
        r';\s*drop\s+table',
        r';\s*delete\s+from',
        r'union\s+select',
        r'--\s*$',
        r'/\*.*\*/',
    ]
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize Input Validator.
        
        Args:
            strict_mode: Whether to apply strict validation rules
        """
        self.strict_mode = strict_mode
    
    def validate_case_text(self, text: str) -> ValidationResult:
        """
        Validate case description text.
        
        Args:
            text: Case description text
            
        Returns:
            ValidationResult object
        """
        violations = []
        risk_score = 0.0
        
        # Check length
        if len(text) > self.MAX_TEXT_LENGTH:
            violations.append(f"Text exceeds maximum length of {self.MAX_TEXT_LENGTH} characters")
            risk_score += 0.3
        
        if len(text) < self.MIN_TEXT_LENGTH:
            violations.append(f"Text too short (minimum {self.MIN_TEXT_LENGTH} characters)")
            risk_score += 0.2
        
        # Check for prompt injection
        injection_found, injection_details = self._check_prompt_injection(text)
        if injection_found:
            violations.append(f"Potential prompt injection detected: {injection_details}")
            risk_score += 0.5
        
        # Check for XSS
        xss_found, xss_details = self._check_xss(text)
        if xss_found:
            violations.append(f"Potential XSS attack detected: {xss_details}")
            risk_score += 0.4
        
        # Check for SQL injection patterns (defensive, though we don't use SQL)
        sql_found, sql_details = self._check_sql_injection(text)
        if sql_found:
            violations.append(f"SQL injection pattern detected: {sql_details}")
            risk_score += 0.3
        
        # Check character distribution
        if self._has_excessive_special_chars(text):
            violations.append("Excessive special characters detected")
            risk_score += 0.2
        
        # Sanitize input
        sanitized = self._sanitize_text(text)
        
        # Determine validity
        is_valid = risk_score < 0.5 and len(violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            sanitized_input=sanitized,
            violations=violations,
            risk_score=min(risk_score, 1.0)
        )
    
    def _check_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """Check for prompt injection attempts."""
        text_lower = text.lower()
        
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return True, f"Pattern '{pattern}' found"
        
        return False, ""
    
    def _check_xss(self, text: str) -> Tuple[bool, str]:
        """Check for XSS attempts."""
        for pattern in self.XSS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return True, f"XSS pattern '{pattern}' found"
        
        return False, ""
    
    def _check_sql_injection(self, text: str) -> Tuple[bool, str]:
        """Check for SQL injection patterns."""
        for pattern in self.SQL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return True, f"SQL pattern '{pattern}' found"
        
        return False, ""
    
    def _has_excessive_special_chars(self, text: str) -> bool:
        """Check if text has excessive special characters."""
        if not text:
            return False
        
        # Count special characters
        special_chars = len(re.findall(r'[^\w\s.,;:!?()\[\]{}\-\'\"\/]', text))
        ratio = special_chars / len(text)
        
        # More than 20% special chars is suspicious
        return ratio > 0.2
    
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text by removing/escaping dangerous patterns.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        sanitized = text
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Remove JavaScript
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Trim
        sanitized = sanitized.strip()
        
        return sanitized
    
    def validate_file_upload(self, filename: str, file_size_bytes: int, content_type: str) -> ValidationResult:
        """
        Validate file uploads.
        
        Args:
            filename: Name of the file
            file_size_bytes: Size in bytes
            content_type: MIME type
            
        Returns:
            ValidationResult object
        """
        violations = []
        risk_score = 0.0
        
        # Check file size
        max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size_bytes > max_size_bytes:
            violations.append(f"File size exceeds {self.MAX_FILE_SIZE_MB}MB limit")
            risk_score += 0.5
        
        # Check file extension
        allowed_extensions = ['.pdf']
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if f'.{file_ext}' not in allowed_extensions:
            violations.append(f"File type .{file_ext} not allowed. Only PDF files accepted.")
            risk_score += 0.6
        
        # Check MIME type
        allowed_mimes = ['application/pdf']
        if content_type not in allowed_mimes:
            violations.append(f"Content type {content_type} not allowed")
            risk_score += 0.4
        
        # Check filename for suspicious patterns
        if re.search(r'[<>:"|?*]', filename):
            violations.append("Filename contains invalid characters")
            risk_score += 0.3
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            violations.append("Potential path traversal detected in filename")
            risk_score += 0.7
        
        is_valid = risk_score < 0.5 and len(violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            sanitized_input=self._sanitize_filename(filename),
            violations=violations,
            risk_score=min(risk_score, 1.0)
        )
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename."""
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename
    
    def validate_agent_selection(self, agents: List[str]) -> ValidationResult:
        """
        Validate agent selection.
        
        Args:
            agents: List of agent names to enable
            
        Returns:
            ValidationResult object
        """
        violations = []
        risk_score = 0.0
        
        valid_agents = ['precedents', 'statutes', 'news', 'bench']
        
        for agent in agents:
            if agent not in valid_agents:
                violations.append(f"Invalid agent: {agent}")
                risk_score += 0.5
        
        is_valid = len(violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            sanitized_input=','.join([a for a in agents if a in valid_agents]),
            violations=violations,
            risk_score=min(risk_score, 1.0)
        )
    
    def validate_parameters(self, params: Dict[str, Any]) -> ValidationResult:
        """
        Validate query parameters.
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            ValidationResult object
        """
        violations = []
        risk_score = 0.0
        
        # Validate k (number of precedents)
        if 'k' in params:
            k = params['k']
            if not isinstance(k, int) or k < 1 or k > 20:
                violations.append("Parameter 'k' must be between 1 and 20")
                risk_score += 0.2
        
        # Validate max_tokens
        if 'max_tokens' in params:
            max_tokens = params['max_tokens']
            if not isinstance(max_tokens, int) or max_tokens < 100 or max_tokens > 4000:
                violations.append("Parameter 'max_tokens' must be between 100 and 4000")
                risk_score += 0.2
        
        # Validate temperature
        if 'temperature' in params:
            temp = params['temperature']
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 1:
                violations.append("Parameter 'temperature' must be between 0 and 1")
                risk_score += 0.2
        
        is_valid = len(violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            sanitized_input=str(params),
            violations=violations,
            risk_score=min(risk_score, 1.0)
        )

