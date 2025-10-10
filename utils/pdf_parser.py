"""
PDF Parser Module
Handles parsing of PDF documents and extraction of legal document metadata.
"""

import re
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document


class LegalPDFParser:
    """Parser for legal PDF documents, specifically Supreme Court judgments."""
    
    def __init__(self):
        pass
    
    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load a PDF file and return its pages.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of Document objects, one per page
        """
        loader = PyPDFLoader(pdf_path)
        return loader.load()
    
    def extract_citation(self, text: str) -> str:
        """
        Extract case citation from text.
        
        Examples:
            [2025] 1 S.C.R. 123 : 2025 INSC 456
            
        Args:
            text: Text to extract citation from
            
        Returns:
            Extracted citation or "Unknown Citation"
        """
        combined = " ".join(text.splitlines())
        
        # Match the full citation: [YEAR] NUMBER S.C.R. NUMBER : YEAR INSC NUMBER
        match = re.search(
            r'\[(\d{4})\]\s*(\d+)\s*S\.C\.R\.\s*(\d+)\s*:\s*(\d{4})\s*INSC\s*(\d+)',
            combined,
            re.IGNORECASE
        )
        if match:
            return f"[{match.group(1)}] {match.group(2)} S.C.R. {match.group(3)} : {match.group(4)} INSC {match.group(5)}"
        
        # Fallback: try to match just the S.C.R. part
        match = re.search(r'\[\d{4}\]\s*\d+\s*S\.C\.R\.\s*\d+', combined, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        
        # Fallback: try to match just the INSC part
        match = re.search(r'\d{4}\s*INSC\s*\d+', combined, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        
        return "Unknown Citation"
    
    def extract_case_title(self, text: str) -> str:
        """
        Extract case title from text.
        
        Example:
            Railway Protection Force & Ors. v. Prem Chand Kumar & Ors.
            
        Args:
            text: Text to extract case title from
            
        Returns:
            Extracted case title or "Unknown Title"
        """
        combined = " ".join(text.splitlines())
        
        # Match case title - appears after citation and before case number (in parentheses)
        # Look for pattern: word(s) v. word(s) followed by opening parenthesis
        match = re.search(
            r'INSC\s+\d+\s+(.+?)\s+v\.?\s+(.+?)(?=\s*\()',
            combined,
            re.IGNORECASE
        )
        if match:
            return f"{match.group(1).strip()} v. {match.group(2).strip()}"
        
        return "Unknown Title"
    
    def extract_case_number(self, text: str) -> str:
        """
        Extract case number from text.
        
        Examples:
            (Civil Appeal No. 11716 of 2025)
            (Criminal Appeal No(s). 3955-3956 of 2025)
            
        Args:
            text: Text to extract case number from
            
        Returns:
            Extracted case number or "Unknown Case Number"
        """
        combined = " ".join(text.splitlines())
        
        # Look for parentheses containing 'No.' or 'No(s).'
        # The pattern handles: No, No., No(s), No(s).
        match = re.search(
            r'\(([^)]*No\.?(?:\(s\))?\.?\s+\d+[^)]*)\)',
            combined,
            re.IGNORECASE
        )
        return match.group(1).strip() if match else "Unknown Case Number"
    
    def extract_judges(self, text: str) -> List[str]:
        """
        Extract judge names from text.
        
        Common patterns:
            [Vikram Nath* and Sandeep Mehta, JJ.]
            [Justice A.B. Smith and Justice C.D. Jones, JJ.]
            
        Args:
            text: Text to extract judge names from
            
        Returns:
            List of judge names
        """
        judges = []
        combined = " ".join(text.splitlines())
        
        # Pattern 1: Supreme Court format with JJ. at end
        # [Name1* and Name2, JJ.] or [Name1, Name2 and Name3,* JJ.]
        # Handle optional asterisks before JJ.
        bracket_match = re.search(
            r'\[([^\]]+),?\s*\*?\s*JJ?\.\]',
            combined,
            re.IGNORECASE
        )
        
        if bracket_match:
            judge_text = bracket_match.group(1)
        else:
            # Pattern 2: Judge names after date in brackets
            # [Decided on: Date] followed by [Judge names]
            bracket_match = re.search(
                r'\[(?:Decided|Date|Judgment).*?\]\s*\[([^\]]+)\]',
                combined,
                re.IGNORECASE
            )
            if bracket_match:
                judge_text = bracket_match.group(1)
            else:
                # Pattern 3: Find judge names with Justice/Hon'ble prefix
                judge_section = re.search(
                    r'(?:Hon\'?ble\s+)?(?:Justice|J\.)\s+[A-Z][a-z]+(?:\s+[A-Z]\.)*(?:\s+[A-Z][a-z]+)+(?:\s+and\s+(?:Hon\'?ble\s+)?(?:Justice|J\.)\s+[A-Z][a-z]+(?:\s+[A-Z]\.)*(?:\s+[A-Z][a-z]+)+)*',
                    combined
                )
                if judge_section:
                    judge_text = judge_section.group(0)
                else:
                    return []
        
        # Extract individual judge names
        # Remove "JJ." or "J." suffix and any trailing asterisks/commas
        judge_text = re.sub(r'[,\*\s]*JJ?\.?\s*$', '', judge_text, flags=re.IGNORECASE)
        judge_text = judge_text.strip(',* ')
        
        # Split by commas first, then handle "and" within parts
        # This handles formats like: "Name1, Name2 and Name3"
        parts = [p.strip() for p in judge_text.split(',')]
        
        final_parts = []
        for part in parts:
            # Further split by "and"
            if ' and ' in part.lower():
                and_parts = re.split(r'\s+and\s+', part, flags=re.IGNORECASE)
                final_parts.extend(and_parts)
            else:
                final_parts.append(part)
        
        for part in final_parts:
            # Remove asterisks, prefixes, and extra whitespace
            name = re.sub(r'\*+', '', part)  # Remove asterisks
            name = re.sub(r'Hon\'?ble\s+|Justice\s+|J\.\s*', '', name, flags=re.IGNORECASE)
            name = name.strip()
            
            # Only keep if it looks like a name (has letters and is not empty)
            if name and len(name) > 2 and not name.lower() in ['jr', 'sr', 'ii', 'iii']:
                judges.append(name)
        
        return judges
    
    def extract_metadata(self, first_page_text: str) -> Dict:
        """
        Extract all metadata from the first page of a legal document.
        
        Args:
            first_page_text: Text content of the first page
            
        Returns:
            Dictionary containing citation, case_title, case_number, and judges
        """
        return {
            "citation": self.extract_citation(first_page_text),
            "case_title": self.extract_case_title(first_page_text),
            "case_number": self.extract_case_number(first_page_text),
            "judges": self.extract_judges(first_page_text)
        }
    
    def parse_pdf(self, pdf_path: str) -> tuple[str, Dict]:
        """
        Parse a PDF file and extract both content and metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (full_text, metadata_dict)
        """
        pages = self.load_pdf(pdf_path)
        
        # Extract metadata from first page (and second page if needed for judges)
        first_page_text = pages[0].page_content
        
        # Sometimes judge names appear on second page
        if len(pages) > 1:
            second_page_text = pages[1].page_content
            combined_text = first_page_text + "\n" + second_page_text[:500]
        else:
            combined_text = first_page_text
        
        metadata = self.extract_metadata(combined_text)
        
        # Combine all pages into one text
        full_text = "\n\n".join([page.page_content for page in pages])
        
        return full_text, metadata
