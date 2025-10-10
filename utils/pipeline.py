"""
Document Processing Pipeline
Orchestrates the entire document processing workflow.
"""

import os
import uuid
from typing import List, Optional
from langchain.docstore.document import Document
from langchain_aws import BedrockEmbeddings
from dotenv import load_dotenv

from .pdf_parser import LegalPDFParser
from .s3_uploader import S3Uploader
from .text_chunker import LegalTextChunker
from .vector_store import VectorStoreManager

load_dotenv()


class DocumentProcessingPipeline:
    """
    End-to-end pipeline for processing legal documents.
    
    Handles:
    1. PDF parsing and metadata extraction
    2. S3 upload (optional)
    3. Text chunking
    4. Embedding and vector storage
    """
    
    def __init__(
        self,
        pdf_dir: str,
        vector_store_dir: str,
        s3_bucket: Optional[str] = None,
        embeddings=None,
        max_chunk_size: int = 2000,
        upload_to_s3: bool = False
    ):
        """
        Initialize the pipeline.
        
        Args:
            pdf_dir: Directory containing PDF files
            vector_store_dir: Directory to save vector store
            s3_bucket: S3 bucket name (optional, required if upload_to_s3=True)
            embeddings: Embedding model (defaults to Bedrock)
            max_chunk_size: Maximum chunk size
            upload_to_s3: Whether to upload PDFs to S3
        """
        self.pdf_dir = pdf_dir
        self.vector_store_dir = vector_store_dir
        self.upload_to_s3_flag = upload_to_s3
        
        # Initialize embeddings
        if embeddings is None:
            embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
        self.embeddings = embeddings
        
        # Initialize components
        self.parser = LegalPDFParser()
        self.chunker = LegalTextChunker(embeddings=embeddings, max_chunk_size=max_chunk_size)
        self.vector_store_manager = VectorStoreManager(
            embeddings=embeddings,
            store_dir=vector_store_dir
        )
        
        # Initialize S3 uploader if needed
        self.s3_uploader = None
        if upload_to_s3:
            if not s3_bucket:
                raise ValueError("s3_bucket must be provided if upload_to_s3=True")
            self.s3_uploader = S3Uploader(bucket_name=s3_bucket)
    
    def process_single_pdf(self, pdf_path: str, filename: str) -> List[Document]:
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            filename: Name of the PDF file
            
        Returns:
            List of Document objects with chunks
        """
        print(f"Processing {filename}...")
        
        # 1. Parse PDF and extract metadata (also get pages for page tracking)
        pages = self.parser.load_pdf(pdf_path)
        full_text, metadata = self.parser.parse_pdf(pdf_path)
        
        # 2. Upload to S3 (optional)
        pdf_url = None
        if self.upload_to_s3_flag and self.s3_uploader:
            s3_key = f"cases/{uuid.uuid4()}.pdf"
            pdf_url = self.s3_uploader.upload_file(pdf_path, s3_key)
            print(f"  ✓ Uploaded to {pdf_url}")
        
        # 3. Chunk the text
        chunks = self.chunker.chunk_text(full_text)
        
        # 4. Create Document objects with page number estimation
        documents = []
        for i, (section_header, chunk_content) in enumerate(chunks):
            # Estimate page number by finding where this chunk appears in the PDF
            page_number = self._estimate_page_number(chunk_content, pages)
            
            doc_metadata = {
                "case_title": metadata["case_title"],
                "citation": metadata["citation"],
                "case_number": metadata["case_number"],
                "judges": metadata.get("judges", []),  # Add judges metadata
                "section": section_header,
                "chunk_id": i,
                "source_file": filename,
                "page_number": page_number,  # Add page number
                "total_pages": len(pages),
            }
            
            # Add PDF URL if uploaded to S3 (use s3_url for consistency)
            if pdf_url:
                doc_metadata["s3_url"] = pdf_url
                doc_metadata["pdf_url"] = pdf_url  # Keep both for compatibility
            
            doc = Document(
                page_content=chunk_content,
                metadata=doc_metadata
            )
            documents.append(doc)
        
        print(f"  ✓ Created {len(chunks)} chunks for {filename}")
        return documents
    
    def _estimate_page_number(self, chunk_content: str, pages: List[Document]) -> int:
        """
        Estimate which page a chunk comes from.
        
        Args:
            chunk_content: The chunk text
            pages: List of page documents
            
        Returns:
            Estimated page number (1-indexed)
        """
        # Take first 100 characters of chunk for matching
        search_text = chunk_content[:100].strip()
        
        # Search through pages to find where this chunk appears
        for page_num, page in enumerate(pages, start=1):
            if search_text in page.page_content:
                return page_num
        
        # If not found, estimate based on chunk position
        # (This is a fallback - shouldn't happen often)
        return 1
    
    def process_all_pdfs(self) -> List[Document]:
        """
        Process all PDF files in the configured directory.
        
        Returns:
            List of all Document objects
        """
        all_documents = []
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith(".pdf")]
        
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_dir}")
            return all_documents
        
        print(f"Found {len(pdf_files)} PDF files to process\n")
        
        # Process each PDF
        for filename in pdf_files:
            pdf_path = os.path.join(self.pdf_dir, filename)
            documents = self.process_single_pdf(pdf_path, filename)
            all_documents.extend(documents)
        
        return all_documents
    
    def run(self):
        """
        Run the complete pipeline: parse, chunk, embed, and store.
        """
        # Process all PDFs
        all_documents = self.process_all_pdfs()
        
        if not all_documents:
            print("No documents to process.")
            return
        
        print(f"\nTotal Chunks: {len(all_documents)}")
        
        # Create and save vector store
        print("\nCreating vector store...")
        self.vector_store_manager.create_vector_store(all_documents)
        self.vector_store_manager.save()
        
        print(f"✅ Vector store created and saved to {self.vector_store_dir}")
    
    def get_vector_store(self):
        """
        Get the vector store (load if not already loaded).
        
        Returns:
            FAISS vector store
        """
        try:
            return self.vector_store_manager.get_vector_store()
        except ValueError:
            # Load from disk if not in memory
            return self.vector_store_manager.load()
