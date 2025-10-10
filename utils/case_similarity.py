"""
Case Similarity Analyzer
Finds similar precedents for a lawyer's current case.
"""

import os
import tempfile
from typing import List, Dict, Any, Union
from langchain.docstore.document import Document
from langchain_aws import BedrockEmbeddings

from .retriever import LegalDocumentRetriever
from .pdf_parser import LegalPDFParser
from .text_chunker import LegalTextChunker
from aws.bedrock_client import call_claude


# System prompt for case similarity analysis
CASE_SIMILARITY_PROMPT = """You are LexiQ, an expert legal case analyzer for lawyers.

TASK:
A lawyer has provided details of their CURRENT CASE. Your job is to analyze the RETRIEVED PRECEDENTS and explain how they relate to this current case.

CURRENT CASE DETAILS:
{current_case}

RETRIEVED SIMILAR PRECEDENTS:
{precedents}

INSTRUCTIONS:
1. Provide a brief summary of the current case's key legal issues
2. For each retrieved precedent, explain:
   - What legal principles it establishes
   - WHY it is relevant to the current case (specific connections)
   - Which arguments it supports
   - Direct quotes from the precedent that apply
   - ALWAYS include page numbers and PDF links
3. Suggest how the lawyer can use these precedents
4. MANDATORY: Include PDF links AND page numbers for every cited case

FORMAT YOUR RESPONSE IN MARKDOWN:

## Case Analysis

### Current Case Summary
[Brief summary of the legal issues in the current case]

### Similar Precedents Found

#### 1. **Case Title (Citation) - Page [PAGE_NUMBER]**
**Relevance Score:** [High/Medium based on similarity]  
**Section:** [Section name]  

**Why This Matters:**
[Explain the specific legal connection to the current case - be detailed and specific]

**Key Legal Principle:**
[What this case established]

**Direct Quote:**
> "Relevant excerpt from the case..."

**How to Use This:**
[Practical advice on applying this precedent]

📄 [View Full Case PDF](PDF_LINK) | Page [PAGE_NUMBER]

---

[Repeat for each precedent]

## Strategic Recommendations
[Overall advice on using these precedents for the current case]

## All References
[List all cases with PDF links]
"""


class CaseSimilarityAnalyzer:
    """Analyzes lawyer's current case and finds similar precedents."""
    
    def __init__(self, vector_store_dir: str = "data/vector_store"):
        """
        Initialize the case similarity analyzer.
        
        Args:
            vector_store_dir: Path to the vector store directory
        """
        self.retriever = LegalDocumentRetriever(vector_store_dir=vector_store_dir)
        self.pdf_parser = LegalPDFParser()
        self.embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
        self.chunker = LegalTextChunker(embeddings=self.embeddings, max_chunk_size=2000)
        self.is_initialized = False
        
    def initialize(self):
        """Load the vector store."""
        print("Initializing Case Similarity Analyzer...")
        self.retriever.load_vector_store()
        self.is_initialized = True
        print("✓ Analyzer ready!\n")
        
    def analyze_case_from_text(
        self, 
        case_description: str, 
        k: int = 5,
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Analyze a case from text description.
        
        Args:
            case_description: Text description of the current case
            k: Number of similar cases to retrieve
            max_tokens: Max tokens for Claude response
            temperature: Sampling temperature
            
        Returns:
            Dictionary with analysis and similar cases
        """
        if not self.is_initialized:
            raise ValueError("Analyzer not initialized. Call initialize() first.")
        
        print(f"🔍 Analyzing case and finding similar precedents...")
        print(f"📝 Case description length: {len(case_description)} characters")
        
        # Retrieve similar cases from vector store
        similar_cases = self.retriever.retrieve(case_description, k=k)
        print(f"✓ Found {len(similar_cases)} similar precedents")
        
        # Format the retrieved precedents
        precedents_context = self.retriever.format_retrieved_docs(similar_cases)
        
        # Build prompt
        prompt = CASE_SIMILARITY_PROMPT.format(
            current_case=case_description,
            precedents=precedents_context
        )
        
        # Get analysis from Claude
        print("🤖 Generating detailed analysis with Claude...")
        analysis = call_claude(prompt, max_tokens=max_tokens, temperature=temperature)
        
        # Get metadata
        metadata = self.retriever.get_metadata_summary(similar_cases)
        
        return {
            "current_case": case_description,
            "analysis": analysis,
            "similar_cases": metadata,
            "num_similar_cases": len(similar_cases)
        }
    
    def analyze_case_from_pdf(
        self,
        pdf_path: str,
        k: int = 5,
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Analyze a case from PDF file.
        
        Args:
            pdf_path: Path to the PDF file of the current case
            k: Number of similar cases to retrieve
            max_tokens: Max tokens for Claude response
            temperature: Sampling temperature
            
        Returns:
            Dictionary with analysis and similar cases
        """
        if not self.is_initialized:
            raise ValueError("Analyzer not initialized. Call initialize() first.")
        
        print(f"📄 Processing PDF: {os.path.basename(pdf_path)}")
        
        # Parse the PDF
        case_text, case_metadata = self.pdf_parser.parse_pdf(pdf_path)
        
        print(f"✓ Extracted case details:")
        print(f"   Title: {case_metadata['case_title']}")
        print(f"   Citation: {case_metadata['citation']}")
        print(f"   Text length: {len(case_text)} characters")
        
        # Create a formatted description including metadata
        case_description = f"""
Case Title: {case_metadata['case_title']}
Citation: {case_metadata['citation']}
Case Number: {case_metadata['case_number']}

Full Text:
{case_text}
"""
        
        # Use text analysis
        result = self.analyze_case_from_text(
            case_description=case_description,
            k=k,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Add PDF metadata to result
        result["pdf_metadata"] = case_metadata
        result["pdf_path"] = pdf_path
        
        return result
    
    def find_similar_cases_only(
        self,
        case_text: str,
        k: int = 10,
        with_scores: bool = True,
        deduplicate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find similar cases without Claude analysis (faster).
        
        Args:
            case_text: Description of the current case
            k: Number of unique similar cases to find
            with_scores: Include similarity scores
            deduplicate: If True, returns k unique cases; if False, returns k chunks
            
        Returns:
            List of similar case metadata
        """
        if not self.is_initialized:
            raise ValueError("Analyzer not initialized. Call initialize() first.")
        
        print(f"🔍 Finding {k} similar {'cases' if deduplicate else 'chunks'}...")
        
        if deduplicate:
            # Retrieve more chunks to ensure we get k unique cases
            # (since multiple chunks may be from the same case)
            retrieval_k = k * 3  # Retrieve 3x to ensure enough unique cases
            
            if with_scores:
                results = self.retriever.retrieve_with_scores(case_text, k=retrieval_k)
            else:
                results = self.retriever.retrieve(case_text, k=retrieval_k)
                # Convert to (doc, score) format for uniform processing
                results = [(doc, 0.0) for doc in results]
            
            # Group chunks by case and keep the best one per case
            cases_dict = {}
            
            for doc, score in results:
                case_id = doc.metadata.get("case_number", doc.metadata.get("case_title", "Unknown"))
                
                # If this case hasn't been seen, or this chunk has a better score
                if case_id not in cases_dict or (with_scores and score < cases_dict[case_id]['score']):
                    case_info = {
                        "case_title": doc.metadata.get("case_title", "Unknown"),
                        "citation": doc.metadata.get("citation", "No citation"),
                        "case_number": doc.metadata.get("case_number", "Unknown"),
                        "section": doc.metadata.get("section", ""),
                        "page_number": doc.metadata.get("page_number", "N/A"),
                        "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                        "s3_url": doc.metadata.get("s3_url", "") or doc.metadata.get("pdf_url", ""),
                        "similarity_score": float(score) if with_scores else None,
                        "content_preview": doc.page_content[:300] + "...",
                        "score": score  # Keep for comparison
                    }
                    cases_dict[case_id] = case_info
                
                # Stop once we have k unique cases
                if len(cases_dict) >= k:
                    break
            
            # Convert to list and remove internal score field
            similar_cases = []
            for case_info in list(cases_dict.values())[:k]:
                case_info.pop('score', None)
                similar_cases.append(case_info)
            
            print(f"✓ Found {len(similar_cases)} unique cases")
            
        else:
            # Original behavior: return k chunks (may have duplicates)
            if with_scores:
                results = self.retriever.retrieve_with_scores(case_text, k=k)
                similar_cases = []
                
                for doc, score in results:
                    case_info = {
                        "case_title": doc.metadata.get("case_title", "Unknown"),
                        "citation": doc.metadata.get("citation", "No citation"),
                        "case_number": doc.metadata.get("case_number", "Unknown"),
                        "section": doc.metadata.get("section", ""),
                        "page_number": doc.metadata.get("page_number", "N/A"),
                        "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                        "s3_url": doc.metadata.get("s3_url", "") or doc.metadata.get("pdf_url", ""),
                        "similarity_score": float(score),
                        "content_preview": doc.page_content[:300] + "..."
                    }
                    similar_cases.append(case_info)
            else:
                results = self.retriever.retrieve(case_text, k=k)
                similar_cases = self.retriever.get_metadata_summary(results)
            
            print(f"✓ Found {len(similar_cases)} chunks")
        
        return similar_cases
    
    def find_similar_cases_with_chunks(
        self,
        case_text: str,
        k_cases: int = 5,
        max_chunks_per_case: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find similar cases and include multiple relevant chunks per case.
        Useful when you want to see all relevant sections of each case.
        
        Args:
            case_text: Description of the current case
            k_cases: Number of unique cases to find
            max_chunks_per_case: Maximum chunks to return per case
            
        Returns:
            List of cases with their relevant chunks grouped together
        """
        if not self.is_initialized:
            raise ValueError("Analyzer not initialized. Call initialize() first.")
        
        print(f"🔍 Finding {k_cases} cases with up to {max_chunks_per_case} chunks each...")
        
        # Retrieve many chunks to find all relevant sections
        retrieval_k = k_cases * max_chunks_per_case * 2
        results = self.retriever.retrieve_with_scores(case_text, k=retrieval_k)
        
        # Group chunks by case
        cases_dict = {}
        
        for doc, score in results:
            case_id = doc.metadata.get("case_number", doc.metadata.get("case_title", "Unknown"))
            
            # Create case entry if doesn't exist
            if case_id not in cases_dict:
                cases_dict[case_id] = {
                    "case_title": doc.metadata.get("case_title", "Unknown"),
                    "citation": doc.metadata.get("citation", "No citation"),
                    "case_number": doc.metadata.get("case_number", "Unknown"),
                    "s3_url": doc.metadata.get("s3_url", "") or doc.metadata.get("pdf_url", ""),
                    "best_score": float(score),
                    "chunks": []
                }
            
            # Add chunk to this case (up to max_chunks_per_case)
            if len(cases_dict[case_id]["chunks"]) < max_chunks_per_case:
                chunk_info = {
                    "section": doc.metadata.get("section", ""),
                    "page_number": doc.metadata.get("page_number", "N/A"),
                    "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                    "similarity_score": float(score),
                    "content_preview": doc.page_content[:300] + "..."
                }
                cases_dict[case_id]["chunks"].append(chunk_info)
            
            # Stop once we have k_cases with enough chunks
            if len(cases_dict) >= k_cases and all(
                len(case["chunks"]) >= max_chunks_per_case 
                for case in list(cases_dict.values())[:k_cases]
            ):
                break
        
        # Convert to list
        similar_cases = list(cases_dict.values())[:k_cases]
        
        total_chunks = sum(len(case["chunks"]) for case in similar_cases)
        print(f"✓ Found {len(similar_cases)} unique cases with {total_chunks} total relevant chunks")
        
        return similar_cases
    
    def compare_cases(
        self,
        case1_text: str,
        case2_text: str,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Compare two cases and find their similarities/differences.
        
        Args:
            case1_text: First case description
            case2_text: Second case description
            max_tokens: Max tokens for response
            
        Returns:
            Comparison analysis
        """
        prompt = f"""You are LexiQ, a legal case comparison expert.

TASK: Compare these two cases and identify:
1. Common legal issues
2. Similar facts or circumstances
3. Different outcomes or reasoning
4. Which precedents might apply to both

CASE 1:
{case1_text}

CASE 2:
{case2_text}

Provide a structured comparison in markdown format."""

        print("🤖 Comparing cases...")
        comparison = call_claude(prompt, max_tokens=max_tokens, temperature=0.3)
        
        return {
            "case1": case1_text[:500] + "...",
            "case2": case2_text[:500] + "...",
            "comparison": comparison
        }

