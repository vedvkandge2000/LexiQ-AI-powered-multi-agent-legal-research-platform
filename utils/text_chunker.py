"""
Text Chunker Module
Handles intelligent chunking of legal documents using header-based and semantic approaches.
"""

import re
from typing import List, Tuple
from langchain_experimental.text_splitter import SemanticChunker
from langchain_aws import BedrockEmbeddings


class LegalTextChunker:
    """
    Chunks legal documents intelligently using header-based and semantic approaches.
    """
    
    # Common section headers in Supreme Court judgments
    LEGAL_SECTION_HEADERS = [
        r'Issue for Consideration',
        r'Headnotes†?',
        r'Held:?',
        r'List of Acts',
        r'List of Keywords',
        r'Case Arising From',
        r'Case Law Cited',
        r'Appearances for Parties',
        r'Judgment\s*/\s*Order of the Supreme Court',
        r'^Judgment$',
        r'^Order$',
        r'^ORDER$',
        r'Conclusion',
        r'Facts',
        r'Analysis',
        r'Reasoning',
        r'Background',
        r'Submissions?',
        r'Discussion',
        r'Ratio Decidendi',
        r'Obiter Dicta',
    ]
    
    def __init__(self, embeddings=None, max_chunk_size: int = 2000):
        """
        Initialize the text chunker.
        
        Args:
            embeddings: Embedding model for semantic chunking (defaults to Bedrock)
            max_chunk_size: Maximum size for chunks before splitting further
        """
        self.max_chunk_size = max_chunk_size
        
        if embeddings is None:
            embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
        
        self.embeddings = embeddings
        self.semantic_splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile"
        )
    
    def header_based_chunk(self, text: str) -> List[Tuple[str, str]]:
        """
        Split text by legal section headers, preserving document structure.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of tuples: (section_header, content)
        """
        chunks = []
        lines = text.split('\n')
        current_header = "Case Introduction"
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if line is a section header
            is_header = False
            matched_header = None
            
            for header_pattern in self.LEGAL_SECTION_HEADERS:
                # Match at the beginning of the line
                if re.match(f'^{header_pattern}', line_stripped, re.IGNORECASE):
                    is_header = True
                    matched_header = line_stripped
                    break
            
            if is_header and matched_header:
                # Save previous section
                if current_content:
                    content_text = '\n'.join(current_content).strip()
                    if content_text:  # Only add if there's actual content
                        chunks.append((current_header, content_text))
                
                # Start new section
                current_header = matched_header
                current_content = []
            else:
                # Add line to current section
                current_content.append(line)
        
        # Add the last section
        if current_content:
            content_text = '\n'.join(current_content).strip()
            if content_text:
                chunks.append((current_header, content_text))
        
        # If no meaningful headers were found, fall back to semantic chunking
        if not chunks or (len(chunks) == 1 and len(text) > self.max_chunk_size):
            semantic_chunks = self.semantic_splitter.split_text(text)
            return [("Section", chunk) for chunk in semantic_chunks]
        
        # Further split large sections using semantic chunking
        final_chunks = []
        for header, content in chunks:
            if len(content) > self.max_chunk_size:
                # Split large sections semantically while preserving header
                sub_chunks = self.semantic_splitter.split_text(content)
                for idx, sub_chunk in enumerate(sub_chunks):
                    sub_header = f"{header} (Part {idx + 1})" if len(sub_chunks) > 1 else header
                    final_chunks.append((sub_header, sub_chunk))
            else:
                final_chunks.append((header, content))
        
        return final_chunks
    
    def chunk_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Main method to chunk text using the appropriate strategy.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of tuples: (section_header, content)
        """
        return self.header_based_chunk(text)
