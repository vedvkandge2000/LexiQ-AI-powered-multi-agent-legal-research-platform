"""
Retriever Module
Handles semantic search and document retrieval from the vector store.
"""

from typing import List, Dict, Any
from langchain.docstore.document import Document
from langchain_aws import BedrockEmbeddings
from .vector_store import VectorStoreManager


class LegalDocumentRetriever:
    """Retrieves relevant legal documents from the vector store."""
    
    def __init__(self, vector_store_dir: str = "data/vector_store"):
        """
        Initialize the retriever.
        
        Args:
            vector_store_dir: Path to the vector store directory
        """
        self.vector_store_manager = VectorStoreManager(store_dir=vector_store_dir)
        self.vector_store = None
        
    def load_vector_store(self):
        """Load the vector store from disk."""
        print("Loading vector store...")
        self.vector_store = self.vector_store_manager.load()
        print("✓ Vector store loaded successfully!")
        
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve the top-k most relevant documents for a query.
        
        Args:
            query: User's search query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant Document objects
        """
        if self.vector_store is None:
            raise ValueError("Vector store not loaded. Call load_vector_store() first.")
        
        # Perform similarity search
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def retrieve_with_scores(self, query: str, k: int = 5) -> List[tuple[Document, float]]:
        """
        Retrieve documents with their relevance scores.
        
        Args:
            query: User's search query
            k: Number of documents to retrieve
            
        Returns:
            List of tuples (Document, score)
        """
        if self.vector_store is None:
            raise ValueError("Vector store not loaded. Call load_vector_store() first.")
        
        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def format_retrieved_docs(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into a readable context string.
        
        Args:
            documents: List of retrieved Document objects
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            content = doc.page_content
            
            # Extract metadata
            case_title = metadata.get("case_title", "Unknown Case")
            citation = metadata.get("citation", "No citation")
            chunk_id = metadata.get("chunk_id", "N/A")
            section = metadata.get("section", "")
            page_number = metadata.get("page_number", "N/A")
            s3_url = metadata.get("s3_url", "") or metadata.get("pdf_url", "")
            
            # Format each document
            doc_string = f"""
---
DOCUMENT {i}
Case: {case_title}
Citation: {citation}
Section: {section if section else 'N/A'}
Page Number: {page_number}
Chunk ID: {chunk_id}
PDF Link: {s3_url if s3_url else 'Not available'}
Content:
{content}
---
"""
            context_parts.append(doc_string)
        
        return "\n".join(context_parts)
    
    def get_metadata_summary(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Extract metadata summary from retrieved documents.
        
        Args:
            documents: List of retrieved Document objects
            
        Returns:
            List of metadata dictionaries
        """
        metadata_list = []
        
        for doc in documents:
            metadata = {
                "case_title": doc.metadata.get("case_title", "Unknown Case"),
                "citation": doc.metadata.get("citation", "No citation"),
                "case_number": doc.metadata.get("case_number", "Unknown"),
                "judges": doc.metadata.get("judges", []),  # Add judges for bench bias analysis
                "section": doc.metadata.get("section", ""),
                "page_number": doc.metadata.get("page_number", "N/A"),
                "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                "s3_url": doc.metadata.get("s3_url", "") or doc.metadata.get("pdf_url", ""),
                "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            metadata_list.append(metadata)
        
        return metadata_list

