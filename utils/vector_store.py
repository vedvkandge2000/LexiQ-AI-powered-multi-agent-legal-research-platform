"""
Vector Store Module
Handles embedding and storage of documents in FAISS vector store.
"""

import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
from langchain.docstore.document import Document


class VectorStoreManager:
    """Manages embedding and storage of documents in FAISS."""
    
    def __init__(self, embeddings=None, store_dir: str = "vector_store"):
        """
        Initialize the vector store manager.
        
        Args:
            embeddings: Embedding model (defaults to Bedrock)
            store_dir: Directory to save the vector store
        """
        if embeddings is None:
            embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
        
        self.embeddings = embeddings
        self.store_dir = store_dir
        self.vector_store = None
        
        # Create directory if it doesn't exist
        os.makedirs(store_dir, exist_ok=True)
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create a new FAISS vector store from documents.
        
        Args:
            documents: List of Document objects to embed
            
        Returns:
            FAISS vector store
        """
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to an existing vector store.
        
        Args:
            documents: List of Document objects to add
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Create one first or load from disk.")
        
        self.vector_store.add_documents(documents)
    
    def save(self, path: str = None):
        """
        Save the vector store to disk.
        
        Args:
            path: Path to save to (defaults to store_dir)
        """
        if self.vector_store is None:
            raise ValueError("No vector store to save. Create one first.")
        
        save_path = path or self.store_dir
        self.vector_store.save_local(save_path)
    
    def load(self, path: str = None) -> FAISS:
        """
        Load a vector store from disk.
        
        Args:
            path: Path to load from (defaults to store_dir)
            
        Returns:
            Loaded FAISS vector store
        """
        load_path = path or self.store_dir
        self.vector_store = FAISS.load_local(
            load_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        return self.vector_store
    
    def get_vector_store(self) -> FAISS:
        """
        Get the current vector store.
        
        Returns:
            Current FAISS vector store
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Create one first or load from disk.")
        
        return self.vector_store
