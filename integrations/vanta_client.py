#!/usr/bin/env python3
"""
Vanta API Client
Handles PII masking job logging and compliance monitoring
"""

import hashlib
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class PIIMaskingResult:
    """Structured result of PII masking operation"""
    original_content_hash: str
    masked_content_hash: str
    pii_types_detected: List[str]
    pii_counts_before: Dict[str, int]
    pii_counts_after: Dict[str, int]
    masking_success: bool
    confidence_score: float
    processing_time_ms: int
    timestamp: datetime
    job_id: str
    case_id: Optional[str] = None
    user_id: Optional[str] = None


class VantaClient:
    """
    Vanta API client for PII masking job logging and compliance monitoring.
    
    Features:
    - OAuth authentication with Vanta
    - SHA-256 hash computation for content integrity
    - Custom resource payload formatting
    - Pass/fail determination based on PII counts
    - Audit logging for compliance
    """
    
    def __init__(self, 
                 client_id: str = None,
                 client_secret: str = None,
                 base_url: str = None):
        """
        Initialize Vanta client.
        
        Args:
            client_id: Vanta OAuth client ID (optional, uses env var if not provided)
            client_secret: Vanta OAuth client secret (optional, uses env var if not provided)
            base_url: Vanta API base URL (optional, uses env var if not provided)
        """
        self.client_id = client_id or os.getenv("VANTA_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("VANTA_CLIENT_SECRET")
        self.base_url = base_url or os.getenv("VANTA_BASE_URL", "https://api.vanta.com")
        self.access_token = None
        self.token_expires_at = None
        
        # API endpoints
        self.auth_endpoint = f"{self.base_url}/oauth/token"
        self.resources_endpoint = f"{self.base_url}/v1/resources"
        self.custom_resources_endpoint = f"{self.base_url}/v1/integrations"
        
        # Initialize authentication
        if self.client_id and self.client_secret:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Vanta using OAuth client credentials.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "vanta-api.all:read vanta-api.all:write"
            }
            
            response = requests.post(
                self.auth_endpoint,
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now(timezone.utc).timestamp() + expires_in
                
                print("✅ Vanta authentication successful")
                return True
            else:
                print(f"❌ Vanta authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Vanta authentication error: {e}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token."""
        if not self.access_token:
            return self._authenticate()
        
        # Check if token is expired (with 5-minute buffer)
        if (self.token_expires_at and 
            datetime.now(timezone.utc).timestamp() > (self.token_expires_at - 300)):
            print("🔄 Vanta token expired, refreshing...")
            return self._authenticate()
        
        return True
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """
        Compute SHA-256 hash of content.
        
        Args:
            content: Text content to hash
            
        Returns:
            SHA-256 hash as hex string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def determine_masking_success(self, 
                                 pii_counts_before: Dict[str, int],
                                 pii_counts_after: Dict[str, int],
                                 threshold: float = 0.95) -> bool:
        """
        Determine if PII masking was successful.
        
        Args:
            pii_counts_before: PII counts before masking
            pii_counts_after: PII counts after masking
            threshold: Success threshold (0.95 = 95% reduction required)
            
        Returns:
            True if masking successful, False otherwise
        """
        total_before = sum(pii_counts_before.values())
        total_after = sum(pii_counts_after.values())
        
        if total_before == 0:
            return True  # No PII to mask
        
        reduction_ratio = (total_before - total_after) / total_before
        return reduction_ratio >= threshold
    
    def structure_pii_masking_payload(self, result: PIIMaskingResult) -> Dict[str, Any]:
        """
        Structure JSON payload for Vanta custom resource.
        
        Args:
            result: PII masking result
            
        Returns:
            Formatted payload for Vanta API
        """
        payload = {
            "resourceType": "PII_MASKING_JOB",
            "resourceId": result.job_id,
            "timestamp": result.timestamp.isoformat(),
            "metadata": {
                "case_id": result.case_id,
                "user_id": result.user_id,
                "processing_time_ms": result.processing_time_ms,
                "confidence_score": result.confidence_score
            },
            "integrity": {
                "original_content_hash": result.original_content_hash,
                "masked_content_hash": result.masked_content_hash,
                "hash_algorithm": "SHA-256"
            },
            "pii_analysis": {
                "types_detected": result.pii_types_detected,
                "counts_before_masking": result.pii_counts_before,
                "counts_after_masking": result.pii_counts_after,
                "total_pii_before": sum(result.pii_counts_before.values()),
                "total_pii_after": sum(result.pii_counts_after.values())
            },
            "compliance": {
                "masking_success": result.masking_success,
                "success_threshold": 0.95,
                "compliance_status": "PASS" if result.masking_success else "FAIL",
                "risk_level": self._assess_risk_level(result.pii_counts_after)
            },
            "audit": {
                "job_type": "PII_MASKING",
                "system": "LexiQ",
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        }
        
        return payload
    
    def _assess_risk_level(self, pii_counts_after: Dict[str, int]) -> str:
        """
        Assess risk level based on remaining PII.
        
        Args:
            pii_counts_after: PII counts after masking
            
        Returns:
            Risk level: LOW, MEDIUM, HIGH, CRITICAL
        """
        total_remaining = sum(pii_counts_after.values())
        
        if total_remaining == 0:
            return "LOW"
        elif total_remaining <= 2:
            return "MEDIUM"
        elif total_remaining <= 5:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def log_pii_masking_result(self, result: PIIMaskingResult) -> Dict[str, Any]:
        """
        Log PII masking result to Vanta as custom resource.
        
        Args:
            result: PII masking result
            
        Returns:
            API response data
        """
        if not self._ensure_authenticated():
            return {
                "success": False,
                "error": "Authentication failed"
            }
        
        try:
            payload = self.structure_pii_masking_payload(result)
            
            response = requests.post(
                self.custom_resources_endpoint,
                json=payload,
                headers=self._get_auth_headers(),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ PII masking result logged to Vanta: {result.job_id}")
                return {
                    "success": True,
                    "resource_id": response.json().get("id"),
                    "job_id": result.job_id,
                    "compliance_status": payload["compliance"]["compliance_status"]
                }
            else:
                print(f"❌ Failed to log to Vanta: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            print(f"❌ Error logging to Vanta: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_compliance_summary(self, 
                              case_id: str = None,
                              user_id: str = None,
                              days: int = 30) -> Dict[str, Any]:
        """
        Get compliance summary from Vanta.
        
        Args:
            case_id: Filter by case ID
            user_id: Filter by user ID
            days: Number of days to look back
            
        Returns:
            Compliance summary data
        """
        if not self._ensure_authenticated():
            return {"success": False, "error": "Authentication failed"}
        
        try:
            params = {
                "resourceType": "PII_MASKING_JOB",
                "days": days
            }
            
            if case_id:
                params["case_id"] = case_id
            if user_id:
                params["user_id"] = user_id
            
            response = requests.get(
                self.custom_resources_endpoint,
                params=params,
                headers=self._get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "summary": self._analyze_compliance_data(data)
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_compliance_data(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze compliance data for summary."""
        total_jobs = len(data)
        successful_jobs = sum(1 for job in data if job.get("compliance", {}).get("masking_success", False))
        
        return {
            "total_jobs": total_jobs,
            "successful_jobs": successful_jobs,
            "success_rate": successful_jobs / total_jobs if total_jobs > 0 else 0,
            "compliance_status": "PASS" if successful_jobs == total_jobs else "FAIL",
            "risk_distribution": self._calculate_risk_distribution(data)
        }
    
    def _calculate_risk_distribution(self, data: List[Dict]) -> Dict[str, int]:
        """Calculate risk level distribution."""
        distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        for job in data:
            risk_level = job.get("compliance", {}).get("risk_level", "UNKNOWN")
            if risk_level in distribution:
                distribution[risk_level] += 1
        
        return distribution


def create_vanta_client() -> VantaClient:
    """Create Vanta client instance."""
    return VantaClient()
