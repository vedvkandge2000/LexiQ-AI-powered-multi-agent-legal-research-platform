#!/usr/bin/env python3
"""
Improved Case Analyzer
Groups chunks by case and creates single analysis per case with all context
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
from aws.bedrock_client import call_claude

# Improved Case Analysis Prompt
CASE_ANALYSIS_PROMPT = """You are a legal research expert analyzing Supreme Court precedents.

TASK:
Analyze the provided current case and the similar precedent cases to provide comprehensive legal insights.

CURRENT CASE:
{current_case}

SIMILAR PRECEDENT CASES:
{precedents_by_case}

ANALYSIS REQUIREMENTS:
1. **Case-by-Case Analysis**: For each precedent case, analyze:
   - Key legal principles established
   - Relevant facts and circumstances
   - Court's reasoning and decision
   - Applicability to current case

2. **Comparative Analysis**: Compare and contrast:
   - Similarities between current case and precedents
   - Key differences in facts or legal issues
   - Evolution of legal principles over time

3. **Strategic Insights**: Provide:
   - Strengths and weaknesses of current case
   - Best arguments based on precedent support
   - Potential counter-arguments to anticipate
   - Recommended legal strategy

4. **Citation Strategy**: Suggest:
   - Most relevant precedents to cite
   - Specific quotes or principles to emphasize
   - How to distinguish unfavorable precedents

FORMAT YOUR RESPONSE AS:
## Case Analysis

### Current Case Summary
[Brief summary of the current case and key legal issues]

### Precedent Analysis

#### Case 1: [Case Title] ([Citation])
**Relevance Score:** [High/Medium/Low]
**Section:** [Section name from metadata]

**Why This Matters:**
[Explanation of why this precedent is relevant]

**Key Legal Principle:**
[Main legal principle established in this case]

**Direct Quote:**
"[Relevant quote from the case content]"

**How to Use This:**
[Specific advice on how to use this precedent]

📄 [View Full Case PDF]([S3 URL]) | Page [Page Number]

[Repeat for each case...]

### Strategic Recommendations
[Overall strategy recommendations based on all precedents]

### All References
[List all cases with citations and PDF links]
"""

class ImprovedCaseAnalyzer:
    """Improved case analyzer that groups chunks by case."""
    
    def __init__(self, retriever):
        """Initialize with a retriever instance."""
        self.retriever = retriever
    
    def analyze_case_with_grouping(
        self, 
        case_description: str, 
        k: int = 10,  # Get more chunks to group
        max_tokens: int = 3000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Analyze case with proper case-level grouping.
        
        Args:
            case_description: Text description of the current case
            k: Number of chunks to retrieve (will be grouped by case)
            max_tokens: Max tokens for Claude response
            temperature: Sampling temperature
            
        Returns:
            Dictionary with grouped analysis
        """
        print(f"🔍 Analyzing case with improved grouping...")
        print(f"📝 Case description length: {len(case_description)} characters")
        
        # Retrieve more chunks to get better case coverage
        chunks = self.retriever.retrieve(case_description, k=k)
        print(f"✓ Retrieved {len(chunks)} chunks")
        
        # Group chunks by case
        cases_grouped = self._group_chunks_by_case(chunks)
        print(f"✓ Grouped into {len(cases_grouped)} unique cases")
        
        # Format grouped cases
        precedents_context = self._format_grouped_cases(cases_grouped)
        
        # Build prompt
        prompt = CASE_ANALYSIS_PROMPT.format(
            current_case=case_description,
            precedents_by_case=precedents_context
        )
        
        # Get analysis from Claude with timeout handling
        print("🤖 Generating comprehensive case analysis with Claude...")
        try:
            analysis = call_claude(
                prompt, 
                max_tokens=max_tokens, 
                temperature=temperature,
                timeout=180  # 3 minutes for complex analysis
            )
        except Exception as e:
            print(f"⚠️ Claude timeout, generating fallback analysis...")
            analysis = self._generate_fallback_analysis(cases_grouped)
        
        # Get case summaries
        case_summaries = self._get_case_summaries(cases_grouped)
        
        return {
            "current_case": case_description,
            "analysis": analysis,
            "cases_found": case_summaries,
            "num_unique_cases": len(cases_grouped),
            "total_chunks": len(chunks)
        }
    
    def _group_chunks_by_case(self, chunks: List) -> Dict[str, List]:
        """Group chunks by case citation/title."""
        cases_grouped = defaultdict(list)
        
        for chunk in chunks:
            metadata = chunk.metadata
            
            # Use citation as primary key, fallback to case_title
            case_key = metadata.get('citation', metadata.get('case_title', 'Unknown'))
            
            # Add chunk to the case group
            cases_grouped[case_key].append({
                'chunk': chunk,
                'metadata': metadata,
                'content': chunk.page_content
            })
        
        return dict(cases_grouped)
    
    def _format_grouped_cases(self, cases_grouped: Dict[str, List]) -> str:
        """Format grouped cases for analysis."""
        formatted_cases = []
        
        for case_key, chunks in cases_grouped.items():
            # Get metadata from first chunk (should be same for all chunks of same case)
            first_metadata = chunks[0]['metadata']
            
            # Combine all content from chunks of this case
            combined_content = []
            for chunk_info in chunks:
                section = chunk_info['metadata'].get('section', '')
                page = chunk_info['metadata'].get('page_number', 'N/A')
                content = chunk_info['content']
                
                if section:
                    combined_content.append(f"[Section: {section}, Page: {page}]\n{content}")
                else:
                    combined_content.append(f"[Page: {page}]\n{content}")
            
            # Format case
            case_title = first_metadata.get('case_title', case_key)
            citation = first_metadata.get('citation', case_key)
            judges = first_metadata.get('judges', [])
            s3_url = first_metadata.get('s3_url', '') or first_metadata.get('pdf_url', '')
            
            case_string = f"""
---
CASE: {case_title}
Citation: {citation}
Judges: {', '.join(judges) if judges else 'N/A'}
PDF: {s3_url}
Number of chunks: {len(chunks)}

COMPLETE CASE CONTENT:
{chr(10).join(combined_content)}
---
"""
            formatted_cases.append(case_string)
        
        return "\n".join(formatted_cases)
    
    def _get_case_summaries(self, cases_grouped: Dict[str, List]) -> List[Dict[str, Any]]:
        """Get summary information for each unique case."""
        summaries = []
        
        for case_key, chunks in cases_grouped.items():
            first_metadata = chunks[0]['metadata']
            
            summary = {
                "case_title": first_metadata.get('case_title', case_key),
                "citation": first_metadata.get('citation', case_key),
                "judges": first_metadata.get('judges', []),
                "s3_url": first_metadata.get('s3_url', '') or first_metadata.get('pdf_url', ''),
                "num_chunks": len(chunks),
                "pages": list(set(chunk['metadata'].get('page_number', 'N/A') for chunk in chunks)),
                "sections": list(set(chunk['metadata'].get('section', '') for chunk in chunks if chunk['metadata'].get('section')))
            }
            summaries.append(summary)
        
        return summaries
    
    def _generate_fallback_analysis(self, cases_grouped: Dict[str, List]) -> str:
        """Generate fallback analysis if Claude times out."""
        analysis = "## Case Analysis\n\n"
        analysis += "### Current Case Summary\n"
        analysis += "Analysis temporarily unavailable due to processing timeout.\n\n"
        
        analysis += "### Precedent Cases Found\n"
        for case_key, chunks in cases_grouped.items():
            first_metadata = chunks[0]['metadata']
            case_title = first_metadata.get('case_title', case_key)
            citation = first_metadata.get('citation', case_key)
            
            analysis += f"#### {case_title} ({citation})\n"
            analysis += f"- **Chunks found:** {len(chunks)}\n"
            analysis += f"- **Pages:** {', '.join(set(str(chunk['metadata'].get('page_number', 'N/A')) for chunk in chunks))}\n"
            analysis += f"- **PDF:** {first_metadata.get('s3_url', 'N/A')}\n\n"
        
        analysis += "### Note\n"
        analysis += "Detailed analysis could not be generated due to processing timeout. "
        analysis += "Please try again or reduce the number of cases retrieved.\n"
        
        return analysis


def create_improved_analyzer(retriever):
    """Create an improved analyzer instance."""
    return ImprovedCaseAnalyzer(retriever)
