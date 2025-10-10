#!/usr/bin/env python3
"""
Bench Bias Agent
Analyzes judge patterns and tendencies based on precedent history.
Extracts judge names from case metadata and analyzes their ruling patterns.
"""

import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from aws.bedrock_client import call_claude


# Judge Analysis Prompt
JUDGE_ANALYSIS_PROMPT = """You are a legal analyst examining judicial patterns.

TASK:
Analyze the following judge's ruling history and provide insights about their tendencies.

JUDGE: {judge_name}
CASES ANALYZED: {num_cases}
RULINGS SUMMARY:
{rulings_summary}

CASE DETAILS:
{case_details}

RULES:
- Identify patterns in the judge's rulings
- Note any consistent stances or tendencies
- Be objective and factual
- Cite specific cases as evidence
- Avoid speculation beyond the data
- If data is limited, state that clearly

FORMAT YOUR RESPONSE AS:
### Justice {judge_name} - Judicial Pattern Analysis

**Cases Reviewed:** {num_cases} relevant cases

**Key Patterns:**
- [Pattern 1 with evidence]
- [Pattern 2 with evidence]

**Notable Tendencies:**
[Description of tendencies based on data]

**Relevant Cases:**
- [Case name] - [Brief ruling summary]

**Analysis Confidence:** [High/Medium/Low based on sample size]
"""


class BenchBiasAgent:
    """Agent for analyzing judge patterns and tendencies from case law."""
    
    # Indian judge title patterns
    JUDGE_PATTERNS = [
        r'(?:Hon\'?ble\s+)?Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:Hon\'?ble\s+)?J\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:Hon\'?ble\s+)?Mr\.\s+Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:Hon\'?ble\s+)?Chief Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'CJI\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    def __init__(self):
        """Initialize the Bench Bias Agent."""
        pass
    
    def extract_judges_from_text(self, text: str) -> List[str]:
        """
        Extract judge names from case text using regex patterns.
        
        Args:
            text: Case text or judgment
            
        Returns:
            List of unique judge names
        """
        judges = set()
        
        for pattern in self.JUDGE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                judge_name = match.group(1).strip()
                # Filter out common false positives
                if len(judge_name) > 2 and judge_name not in ['The', 'Court', 'Bench']:
                    judges.add(judge_name)
        
        return sorted(list(judges))
    
    def extract_judges_from_cases(self, similar_cases: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract judge names from a list of similar cases with metadata.
        
        Args:
            similar_cases: List of case dictionaries from case similarity search
            
        Returns:
            Dictionary mapping judge names to their cases
        """
        judge_cases = defaultdict(list)
        
        for case in similar_cases:
            # Check metadata for judge names
            judges = []
            
            # Try to get from metadata (primary source)
            if 'judges' in case and case['judges']:
                if isinstance(case['judges'], list):
                    judges = case['judges']
                elif isinstance(case['judges'], str):
                    judges = [case['judges']]
            
            # If not in metadata, try extracting from content as fallback
            if not judges and 'content_preview' in case:
                judges = self.extract_judges_from_text(case['content_preview'])
            
            # If still not found, try from full content if available
            if not judges and 'content' in case:
                judges = self.extract_judges_from_text(case['content'][:1000])
            
            # Add case to each judge
            for judge in judges:
                # Clean judge name
                judge = judge.strip()
                if judge:
                    judge_cases[judge].append({
                        'case_title': case.get('case_title', 'Unknown'),
                        'citation': case.get('citation', 'N/A'),
                        'case_number': case.get('case_number', 'N/A'),
                        'page_number': case.get('page_number', 'N/A'),
                        'content': case.get('content_preview', '')[:300]
                    })
        
        return dict(judge_cases)
    
    def analyze_judge_pattern(self, 
                             judge_name: str, 
                             cases: List[Dict[str, str]],
                             max_tokens: int = 1500) -> str:
        """
        Analyze a judge's pattern using Claude.
        
        Args:
            judge_name: Name of the judge
            cases: List of cases involving this judge
            max_tokens: Maximum tokens for Claude response
            
        Returns:
            Analysis text
        """
        if not cases:
            return f"### Justice {judge_name}\n\nNo cases found for pattern analysis."
        
        # Prepare case details
        case_details = ""
        for i, case in enumerate(cases[:10], 1):  # Limit to 10 cases
            case_details += f"\n{i}. **{case['case_title']}** ({case['citation']})\n"
            case_details += f"   {case['content'][:200]}...\n"
        
        # Create rulings summary
        rulings_summary = f"Found in {len(cases)} cases in the knowledge base"
        
        prompt = JUDGE_ANALYSIS_PROMPT.format(
            judge_name=judge_name,
            num_cases=len(cases),
            rulings_summary=rulings_summary,
            case_details=case_details
        )
        
        analysis = call_claude(prompt, max_tokens=max_tokens, temperature=0.3)
        return analysis
    
    def analyze_bench_from_cases(self, 
                                 similar_cases: List[Dict[str, Any]],
                                 max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Complete pipeline: extract judges and analyze patterns.
        
        Args:
            similar_cases: List of similar cases from precedent search
            max_tokens: Maximum tokens for Claude analysis
            
        Returns:
            Dictionary with judge analysis
        """
        print("🔍 Extracting judges from precedent cases...")
        
        # Extract judges
        judge_cases = self.extract_judges_from_cases(similar_cases)
        
        if not judge_cases:
            return {
                "judges": {},
                "analysis": "## No Judges Identified\n\nNo judge names were found in the precedent cases.",
                "num_judges": 0
            }
        
        print(f"✓ Found {len(judge_cases)} judges in precedents")
        
        # Sort judges by number of cases (most active first)
        sorted_judges = sorted(judge_cases.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Analyze top judges
        analyses = []
        top_judges = sorted_judges[:5]  # Analyze top 5 judges
        
        print("🤖 Analyzing judicial patterns...")
        
        for judge_name, cases in top_judges:
            print(f"   Analyzing Justice {judge_name}...")
            analysis = self.analyze_judge_pattern(judge_name, cases, max_tokens=max_tokens//len(top_judges))
            analyses.append(analysis)
        
        # Combine analyses
        full_analysis = "# Bench Bias Analysis\n\n"
        full_analysis += f"Analyzed {len(judge_cases)} judges from {len(similar_cases)} precedent cases.\n\n"
        full_analysis += "---\n\n"
        full_analysis += "\n\n---\n\n".join(analyses)
        
        # Summary statistics
        judge_summary = {}
        for judge_name, cases in judge_cases.items():
            judge_summary[judge_name] = {
                'num_cases': len(cases),
                'cases': cases
            }
        
        print("✓ Bench analysis complete")
        
        return {
            "judges": judge_summary,
            "analysis": full_analysis,
            "num_judges": len(judge_cases),
            "top_judges": [j[0] for j in top_judges]
        }
    
    def quick_judge_extraction(self, similar_cases: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Quick extraction of judges and case counts without analysis.
        
        Args:
            similar_cases: List of similar cases
            
        Returns:
            Dictionary mapping judge names to case counts
        """
        judge_cases = self.extract_judges_from_cases(similar_cases)
        return {judge: len(cases) for judge, cases in judge_cases.items()}
    
    def get_judge_statistics(self, judge_cases: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Get statistical summary of judges.
        
        Args:
            judge_cases: Dictionary of judge to cases mapping
            
        Returns:
            Statistics dictionary
        """
        if not judge_cases:
            return {}
        
        stats = {
            'total_judges': len(judge_cases),
            'total_cases': sum(len(cases) for cases in judge_cases.values()),
            'most_active_judge': max(judge_cases.items(), key=lambda x: len(x[1]))[0],
            'case_distribution': {judge: len(cases) for judge, cases in judge_cases.items()}
        }
        
        return stats

