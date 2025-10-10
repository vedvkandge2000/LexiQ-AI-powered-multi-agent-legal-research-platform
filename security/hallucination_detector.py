#!/usr/bin/env python3
"""
Hallucination Detector Module
Detects fake precedents, articles, and statutes in LLM outputs.
Validates references against vector store and known legal databases.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Reference:
    """Container for a legal reference."""
    ref_type: str  # 'case', 'statute', 'article'
    text: str
    section: Optional[str] = None
    act_name: Optional[str] = None
    citation: Optional[str] = None
    position: int = 0


@dataclass
class HallucinationResult:
    """Container for hallucination detection result."""
    is_hallucination: bool
    reference: Reference
    confidence: float
    reason: str
    validated_against_index: bool
    matched_statute: bool


class HallucinationDetector:
    """
    Detects hallucinations in LLM outputs by validating legal references.
    
    Validates:
    - Case precedents (citations, case names)
    - Statutory references (IPC, CrPC, CPC sections)
    - Constitutional articles
    - Legal provisions
    """
    
    # Known Indian legal statutes with valid section ranges
    KNOWN_STATUTES = {
        'ipc': {
            'full_name': 'Indian Penal Code, 1860',
            'valid_sections': set(range(1, 512)),  # Sections 1-511
            'special_sections': ['498A', '376A', '376B', '376C', '376D']
        },
        'crpc': {
            'full_name': 'Code of Criminal Procedure, 1973',
            'valid_sections': set(range(1, 485)),  # Sections 1-484
            'special_sections': []
        },
        'cpc': {
            'full_name': 'Code of Civil Procedure, 1908',
            'valid_sections': set(range(1, 159)),  # Sections 1-158
            'special_sections': []
        },
        'it_act': {
            'full_name': 'Information Technology Act, 2000',
            'valid_sections': set(range(1, 88)),  # Sections 1-87
            'special_sections': ['66A', '66B', '66C', '66D', '66E', '66F']
        },
        'evidence_act': {
            'full_name': 'Indian Evidence Act, 1872',
            'valid_sections': set(range(1, 168)),  # Sections 1-167
            'special_sections': []
        },
        'constitution': {
            'full_name': 'Constitution of India',
            'valid_sections': set(range(1, 396)),  # Articles 1-395
            'special_sections': ['12A', '21A', '35A', '51A', '371A', '371B']
        }
    }
    
    # Patterns for extracting references
    REFERENCE_PATTERNS = {
        'case_citation': [
            r'\[(\d{4})\]\s*\d+\s*S\.C\.R\.\s*\d+',  # [2025] 1 S.C.R. 123
            r'\d{4}\s*INSC\s*\d+',  # 2025 INSC 456
            r'\d{4}\s*SCC\s*\d+',  # 2025 SCC 123
        ],
        'ipc_section': [
            r'Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?IPC',
            r'IPC\s+Section\s+(\d+[A-Z]?)',
            r's\.?\s*(\d+[A-Z]?)\s+IPC',
        ],
        'crpc_section': [
            r'Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?Cr\.?P\.?C',
            r'Cr\.?P\.?C\.?\s+Section\s+(\d+[A-Z]?)',
        ],
        'cpc_section': [
            r'Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?C\.?P\.?C',
            r'C\.?P\.?C\.?\s+Section\s+(\d+[A-Z]?)',
        ],
        'article': [
            r'Article\s+(\d+[A-Z]?)\s+of\s+(?:the\s+)?Constitution',
            r'Article\s+(\d+[A-Z]?)',
        ],
        'it_act_section': [
            r'Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?IT\s+Act',
        ],
    }
    
    def __init__(self, retriever=None, log_file: str = "security/logs/hallucination_audit.log"):
        """
        Initialize Hallucination Detector.
        
        Args:
            retriever: LegalDocumentRetriever for validating against vector store
            log_file: Path to hallucination audit log
        """
        self.retriever = retriever
        self._setup_logging(log_file)
    
    def _setup_logging(self, log_file: str):
        """Setup hallucination audit logging."""
        self.logger = logging.getLogger('LexiQ.Hallucination')
        self.logger.setLevel(logging.INFO)
        
        try:
            import os
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup hallucination logging: {e}")
    
    def extract_references(self, text: str) -> List[Reference]:
        """
        Extract all legal references from text.
        
        Args:
            text: LLM output text
            
        Returns:
            List of Reference objects
        """
        references = []
        
        # Extract case citations
        for pattern in self.REFERENCE_PATTERNS['case_citation']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                references.append(Reference(
                    ref_type='case',
                    text=match.group(0),
                    citation=match.group(0),
                    position=match.start()
                ))
        
        # Extract IPC sections
        for pattern in self.REFERENCE_PATTERNS['ipc_section']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                section = match.group(1) if match.lastindex >= 1 else None
                references.append(Reference(
                    ref_type='statute',
                    text=match.group(0),
                    section=section,
                    act_name='IPC',
                    position=match.start()
                ))
        
        # Extract CrPC sections
        for pattern in self.REFERENCE_PATTERNS['crpc_section']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                section = match.group(1) if match.lastindex >= 1 else None
                references.append(Reference(
                    ref_type='statute',
                    text=match.group(0),
                    section=section,
                    act_name='CrPC',
                    position=match.start()
                ))
        
        # Extract CPC sections
        for pattern in self.REFERENCE_PATTERNS['cpc_section']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                section = match.group(1) if match.lastindex >= 1 else None
                references.append(Reference(
                    ref_type='statute',
                    text=match.group(0),
                    section=section,
                    act_name='CPC',
                    position=match.start()
                ))
        
        # Extract Articles
        for pattern in self.REFERENCE_PATTERNS['article']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                article_num = match.group(1)
                references.append(Reference(
                    ref_type='article',
                    text=match.group(0),
                    section=article_num,
                    act_name='Constitution',
                    position=match.start()
                ))
        
        # Extract IT Act sections
        for pattern in self.REFERENCE_PATTERNS['it_act_section']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                section = match.group(1) if match.lastindex >= 1 else None
                references.append(Reference(
                    ref_type='statute',
                    text=match.group(0),
                    section=section,
                    act_name='IT_Act',
                    position=match.start()
                ))
        
        return references
    
    def validate_statute(self, reference: Reference) -> Tuple[bool, str]:
        """
        Validate a statutory reference against known statutes.
        
        Args:
            reference: Reference object
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if reference.ref_type != 'statute' and reference.ref_type != 'article':
            return True, "Not a statute reference"
        
        if not reference.section:
            return True, "No section to validate"
        
        # Map act name to statute key
        act_map = {
            'IPC': 'ipc',
            'CrPC': 'crpc',
            'CPC': 'cpc',
            'IT_Act': 'it_act',
            'Evidence_Act': 'evidence_act',
            'Constitution': 'constitution'
        }
        
        statute_key = act_map.get(reference.act_name)
        if not statute_key:
            return True, f"Unknown act: {reference.act_name}"
        
        statute_info = self.KNOWN_STATUTES.get(statute_key)
        if not statute_info:
            return True, "Statute not in database"
        
        # Check if section is valid
        section_str = reference.section
        
        # Check special sections first (like 498A, 66A)
        if section_str in statute_info['special_sections']:
            return True, f"Valid special section {section_str}"
        
        # Try to parse as integer
        try:
            section_num = int(re.match(r'\d+', section_str).group())
            if section_num in statute_info['valid_sections']:
                return True, f"Valid section {section_num}"
            else:
                return False, f"Section {section_num} does not exist in {statute_info['full_name']}"
        except:
            return False, f"Invalid section format: {section_str}"
    
    def validate_case_citation(self, reference: Reference) -> Tuple[bool, str]:
        """
        Validate a case citation against vector store.
        
        Args:
            reference: Reference object
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if reference.ref_type != 'case':
            return True, "Not a case reference"
        
        if not self.retriever:
            return True, "No retriever available for validation"
        
        # Search vector store for this citation
        try:
            results = self.retriever.retrieve(reference.citation, k=3)
            
            # Check if any result matches the citation
            for result in results:
                result_citation = result.metadata.get('citation', '')
                if self._citations_match(reference.citation, result_citation):
                    return True, f"Found in vector store: {result_citation}"
            
            return False, "Citation not found in vector store"
            
        except Exception as e:
            return True, f"Error validating: {str(e)}"
    
    def _citations_match(self, citation1: str, citation2: str) -> bool:
        """Check if two citations match (fuzzy)."""
        # Normalize citations
        c1 = re.sub(r'\s+', ' ', citation1.lower().strip())
        c2 = re.sub(r'\s+', ' ', citation2.lower().strip())
        
        # Extract key numbers
        nums1 = set(re.findall(r'\d+', c1))
        nums2 = set(re.findall(r'\d+', c2))
        
        # If most numbers match, consider it a match
        if nums1 and nums2:
            overlap = len(nums1 & nums2) / max(len(nums1), len(nums2))
            return overlap >= 0.7
        
        return False
    
    def detect_hallucinations(self, 
                             input_query: str,
                             output_text: str,
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method to detect hallucinations in LLM output.
        
        Args:
            input_query: Original user query
            output_text: LLM generated output
            user_id: Optional user identifier
            
        Returns:
            Dictionary with hallucination detection results
        """
        # Extract references
        references = self.extract_references(output_text)
        
        if not references:
            return {
                'has_hallucinations': False,
                'num_references': 0,
                'suspected_fake_refs': [],
                'confidence_score': 1.0,
                'summary': 'No references found to validate'
            }
        
        # Validate each reference
        hallucination_results = []
        
        for ref in references:
            if ref.ref_type == 'case':
                validated_index, reason = self.validate_case_citation(ref)
                matched_statute = False
            else:
                matched_statute, reason = self.validate_statute(ref)
                validated_index = True  # Statutes validated against known database
            
            is_hallucination = not (validated_index and matched_statute)
            
            # Calculate confidence
            confidence = 0.5
            if not is_hallucination:
                confidence = 0.9
            elif "not found" in reason.lower():
                confidence = 0.8
            elif "does not exist" in reason.lower():
                confidence = 0.95
            
            result = HallucinationResult(
                is_hallucination=is_hallucination,
                reference=ref,
                confidence=confidence,
                reason=reason,
                validated_against_index=validated_index,
                matched_statute=matched_statute if ref.ref_type != 'case' else True
            )
            
            if is_hallucination:
                hallucination_results.append(result)
        
        # Calculate overall confidence
        if hallucination_results:
            avg_confidence = sum(r.confidence for r in hallucination_results) / len(hallucination_results)
        else:
            avg_confidence = 1.0
        
        # Prepare suspected fake references
        suspected_fakes = [
            {
                'type': r.reference.ref_type,
                'text': r.reference.text,
                'reason': r.reason,
                'confidence': round(r.confidence, 3),
                'validated_against_index': r.validated_against_index,
                'matched_statute': r.matched_statute
            }
            for r in hallucination_results
        ]
        
        # Log if hallucinations detected
        if hallucination_results:
            self._log_hallucination(
                input_query=input_query,
                output_text=output_text,
                suspected_fakes=suspected_fakes,
                confidence_score=avg_confidence,
                user_id=user_id
            )
        
        return {
            'has_hallucinations': len(hallucination_results) > 0,
            'num_references': len(references),
            'num_suspected': len(hallucination_results),
            'suspected_fake_refs': suspected_fakes,
            'confidence_score': round(avg_confidence, 3),
            'summary': self._generate_summary(references, hallucination_results)
        }
    
    def _generate_summary(self, 
                         all_refs: List[Reference], 
                         hallucinations: List[HallucinationResult]) -> str:
        """Generate human-readable summary."""
        if not hallucinations:
            return f"All {len(all_refs)} references validated successfully."
        
        return (f"⚠️ Found {len(hallucinations)} suspected hallucination(s) "
                f"out of {len(all_refs)} total references. "
                f"Please verify these references independently.")
    
    def _log_hallucination(self,
                          input_query: str,
                          output_text: str,
                          suspected_fakes: List[Dict],
                          confidence_score: float,
                          user_id: Optional[str]):
        """Log suspected hallucination."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id or 'anonymous',
            'suspected_hallucination': True,
            'input_query': input_query[:200] + '...' if len(input_query) > 200 else input_query,
            'output_text': output_text[:500] + '...' if len(output_text) > 500 else output_text,
            'suspected_fake_refs': suspected_fakes,
            'confidence_score': confidence_score,
            'num_suspected': len(suspected_fakes)
        }
        
        self.logger.warning(json.dumps(log_entry))

