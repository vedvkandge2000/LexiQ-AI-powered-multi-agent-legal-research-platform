#!/usr/bin/env python3
"""
Statute Reference Agent
Extracts legal sections, articles, and acts from case text.
Provides plain-English explanations using Claude.
"""

import re
from typing import Dict, List, Any, Set
from aws.bedrock_client import call_claude


# Statute Explanation Prompt
STATUTE_EXPLANATION_PROMPT = """You are a legal expert explaining Indian law in plain English.

TASK:
Explain the following legal provisions in simple, clear language that a non-lawyer can understand.

RULES:
- Use plain English, avoid excessive legal jargon
- Explain what the provision does, not just what it says
- Provide context about when it applies
- Be concise (2-3 sentences per provision)
- If you don't have information about a provision, say so clearly

PROVISIONS TO EXPLAIN:
{provisions}

FORMAT YOUR RESPONSE AS:
### [Provision Name]
**What it means:** [Plain English explanation]
**When it applies:** [Context/scenarios]
**Key points:** [Brief bullet points if needed]

---
"""


class StatuteReferenceAgent:
    """Agent for extracting and explaining legal statutes, acts, and articles."""
    
    # Indian legal provision patterns
    PATTERNS = {
        'article': [
            r'\bArticle\s+(\d+[A-Z]?(?:\s*\(\d+\))?)',  # Article 21, Article 14(1)
            r'\bArt\.?\s+(\d+[A-Z]?(?:\s*\(\d+\))?)',   # Art. 21, Art 21
        ],
        'section': [
            r'\bSection\s+(\d+[A-Z]?(?:\s*\(\d+\))?)',  # Section 302, Section 498A
            r'\bSec\.?\s+(\d+[A-Z]?(?:\s*\(\d+\))?)',   # Sec. 302, Sec 302
            r'\bs\.?\s+(\d+[A-Z]?(?:\s*\(\d+\))?)\b',   # s. 302, s 302
        ],
        'ipc': [
            r'\bIPC\s+(?:Section\s+)?(\d+[A-Z]?)',      # IPC 302, IPC Section 302
            r'\bIndian\s+Penal\s+Code.*?Section\s+(\d+[A-Z]?)',
        ],
        'crpc': [
            r'\bCr\.?P\.?C\.?\s+(?:Section\s+)?(\d+[A-Z]?)',  # CrPC 154, Cr.P.C. 154
            r'\bCode\s+of\s+Criminal\s+Procedure.*?Section\s+(\d+[A-Z]?)',
        ],
        'cpc': [
            r'\bC\.?P\.?C\.?\s+(?:Section\s+)?(\d+[A-Z]?)',   # CPC 115, C.P.C. 115
            r'\bCivil\s+Procedure\s+Code.*?Section\s+(\d+[A-Z]?)',
        ],
        'it_act': [
            r'\bIT\s+Act\s+(?:Section\s+)?(\d+[A-Z]?)',  # IT Act 66A
            r'\bInformation\s+Technology\s+Act.*?Section\s+(\d+[A-Z]?)',
        ],
        'evidence_act': [
            r'\bEvidence\s+Act\s+(?:Section\s+)?(\d+[A-Z]?)',
            r'\bIndian\s+Evidence\s+Act.*?Section\s+(\d+[A-Z]?)',
        ],
        'cgst': [
            r'\bCGST\s+Act\s+(?:Section\s+)?(\d+[A-Z]?)',
            r'\bCentral\s+Goods\s+and\s+Services\s+Tax.*?Section\s+(\d+[A-Z]?)',
        ],
    }
    
    # Known acts and their full names
    ACT_NAMES = {
        'ipc': 'Indian Penal Code, 1860',
        'crpc': 'Code of Criminal Procedure, 1973',
        'cpc': 'Code of Civil Procedure, 1908',
        'it_act': 'Information Technology Act, 2000',
        'evidence_act': 'Indian Evidence Act, 1872',
        'cgst': 'Central Goods and Services Tax Act, 2017',
        'article': 'Constitution of India',
    }
    
    def __init__(self):
        """Initialize the Statute Reference Agent."""
        pass
    
    def extract_provisions(self, text: str) -> Dict[str, List[str]]:
        """
        Extract legal provisions from text using regex patterns.
        
        Args:
            text: Case text or legal document
            
        Returns:
            Dictionary with provision types and extracted references
        """
        provisions = {}
        
        for provision_type, patterns in self.PATTERNS.items():
            found = set()
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Extract the number/reference
                    ref = match.group(1).strip()
                    found.add(ref)
            
            if found:
                provisions[provision_type] = sorted(list(found))
        
        return provisions
    
    def format_provisions(self, provisions: Dict[str, List[str]]) -> List[str]:
        """
        Format extracted provisions into readable strings.
        
        Args:
            provisions: Dictionary of extracted provisions
            
        Returns:
            List of formatted provision strings
        """
        formatted = []
        
        for prov_type, refs in provisions.items():
            act_name = self.ACT_NAMES.get(prov_type, prov_type.replace('_', ' ').title())
            
            for ref in refs:
                if prov_type == 'article':
                    formatted.append(f"Article {ref} of the Constitution of India")
                elif prov_type == 'section':
                    formatted.append(f"Section {ref}")
                elif prov_type == 'ipc':
                    formatted.append(f"Section {ref} of IPC (Indian Penal Code, 1860)")
                elif prov_type == 'crpc':
                    formatted.append(f"Section {ref} of CrPC (Code of Criminal Procedure, 1973)")
                elif prov_type == 'cpc':
                    formatted.append(f"Section {ref} of CPC (Code of Civil Procedure, 1908)")
                elif prov_type == 'it_act':
                    formatted.append(f"Section {ref} of IT Act (Information Technology Act, 2000)")
                elif prov_type == 'evidence_act':
                    formatted.append(f"Section {ref} of Indian Evidence Act, 1872")
                elif prov_type == 'cgst':
                    formatted.append(f"Section {ref} of CGST Act, 2017")
                else:
                    formatted.append(f"Section {ref} of {act_name}")
        
        return formatted
    
    def explain_provisions(self, provisions_list: List[str], max_tokens: int = 2000) -> str:
        """
        Generate plain-English explanations for extracted provisions using Claude.
        
        Args:
            provisions_list: List of formatted provision strings
            max_tokens: Maximum tokens for Claude response
            
        Returns:
            Markdown-formatted explanations
        """
        if not provisions_list:
            return "## No Legal Provisions Found\n\nNo specific legal provisions were identified in the text."
        
        # Limit to avoid overwhelming Claude
        if len(provisions_list) > 15:
            provisions_list = provisions_list[:15]
            note = "\n\n*Note: Showing first 15 provisions. Additional provisions were found but not explained to keep the response concise.*"
        else:
            note = ""
        
        provisions_text = "\n".join([f"- {prov}" for prov in provisions_list])
        
        prompt = STATUTE_EXPLANATION_PROMPT.format(provisions=provisions_text)
        
        explanation = call_claude(prompt, max_tokens=max_tokens, temperature=0.3)
        
        return explanation + note
    
    def analyze_statutes(self, case_text: str, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Complete pipeline: extract provisions and generate explanations.
        
        Args:
            case_text: The case description or document text
            max_tokens: Maximum tokens for Claude explanation
            
        Returns:
            Dictionary with extracted provisions and explanations
        """
        print("🔍 Extracting legal provisions...")
        
        # Extract provisions
        provisions = self.extract_provisions(case_text)
        
        if not provisions:
            return {
                "provisions": {},
                "provisions_list": [],
                "explanation": "## No Legal Provisions Found\n\nNo specific legal provisions were identified in the case text.",
                "num_provisions": 0
            }
        
        # Format provisions
        provisions_list = self.format_provisions(provisions)
        
        print(f"✓ Found {len(provisions_list)} legal provisions")
        print("🤖 Generating plain-English explanations...")
        
        # Get explanations
        explanation = self.explain_provisions(provisions_list, max_tokens=max_tokens)
        
        print("✓ Analysis complete")
        
        return {
            "provisions": provisions,
            "provisions_list": provisions_list,
            "explanation": explanation,
            "num_provisions": len(provisions_list)
        }
    
    def quick_extract(self, case_text: str) -> Dict[str, List[str]]:
        """
        Quick extraction without Claude explanations.
        
        Args:
            case_text: The case text
            
        Returns:
            Dictionary of extracted provisions
        """
        return self.extract_provisions(case_text)
    
    def extract_specific_act(self, case_text: str, act_type: str) -> List[str]:
        """
        Extract provisions from a specific act only.
        
        Args:
            case_text: The case text
            act_type: Type of act (ipc, crpc, article, etc.)
            
        Returns:
            List of extracted references
        """
        if act_type not in self.PATTERNS:
            return []
        
        found = set()
        patterns = self.PATTERNS[act_type]
        
        for pattern in patterns:
            matches = re.finditer(pattern, case_text, re.IGNORECASE)
            for match in matches:
                found.add(match.group(1).strip())
        
        return sorted(list(found))
    
    def get_summary(self, provisions: Dict[str, List[str]]) -> str:
        """
        Get a summary of extracted provisions.
        
        Args:
            provisions: Dictionary of extracted provisions
            
        Returns:
            Summary string
        """
        if not provisions:
            return "No legal provisions found."
        
        summary_parts = []
        for prov_type, refs in provisions.items():
            act_name = self.ACT_NAMES.get(prov_type, prov_type.replace('_', ' ').title())
            summary_parts.append(f"{len(refs)} from {act_name}")
        
        return f"Found {sum(len(refs) for refs in provisions.values())} provisions: " + ", ".join(summary_parts)

