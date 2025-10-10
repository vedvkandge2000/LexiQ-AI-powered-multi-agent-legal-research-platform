"""
Query Handler Module
Orchestrates retrieval and response generation using Claude.
"""

from typing import Dict, List, Any
from .retriever import LegalDocumentRetriever
from aws.bedrock_client import call_claude


# LexiQ System Prompt
LEXIQ_SYSTEM_PROMPT = """You are LexiQ, a Supreme Court case law assistant.

TASK:
Answer the user's query using the retrieved case chunks.

RULES:
- ALWAYS include case title, official citation, page number, and section reference.
- Quote DIRECT excerpts (2-3 lines) from the retrieved content.
- MANDATORY: Include PDF links AND page numbers for EVERY case cited using the exact information from the context.
- If multiple cases are relevant, list them clearly.
- Be concise and precise.
- Use legal terminology appropriately but explain complex concepts.
- For each precedent, explain WHY it is relevant (chain-of-thought reasoning).

FORMAT YOUR RESPONSE IN MARKDOWN:
## Summary
Concise plain-English explanation for the lawyer.

## Relevant Precedents
1. **Case Title (Citation) - Page [PAGE_NUMBER]**  
   **Section:** [Section name from context]  
   **Why Relevant:** [Explain the connection to the query]  
   **Key Excerpt:**  
   > "Direct quote from the retrieved content..."  
   
   📄 [View Full Case PDF](PDF_LINK_FROM_CONTEXT) | Page [PAGE_NUMBER]

## References
List all citations with their page numbers and PDF links again."""


class QueryHandler:
    """Handles user queries by retrieving relevant documents and generating responses."""
    
    def __init__(self, vector_store_dir: str = "data/vector_store", k: int = 5):
        """
        Initialize the query handler.
        
        Args:
            vector_store_dir: Path to the vector store directory
            k: Number of documents to retrieve per query
        """
        self.retriever = LegalDocumentRetriever(vector_store_dir=vector_store_dir)
        self.k = k
        self.is_initialized = False
        
    def initialize(self):
        """Load the vector store and prepare for queries."""
        print("Initializing LexiQ Query Handler...")
        self.retriever.load_vector_store()
        self.is_initialized = True
        print("✓ Query Handler ready!\n")
        
    def query(self, user_query: str, max_tokens: int = 1500, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Process a user query and generate a response.
        
        Args:
            user_query: The user's legal question
            max_tokens: Maximum tokens for Claude's response
            temperature: Sampling temperature for Claude
            
        Returns:
            Dictionary containing response and metadata
        """
        if not self.is_initialized:
            raise ValueError("Query handler not initialized. Call initialize() first.")
        
        print(f"🔍 Searching for: {user_query}")
        
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(user_query, k=self.k)
        print(f"✓ Retrieved {len(retrieved_docs)} relevant documents")
        
        # Step 2: Format context for Claude
        context = self.retriever.format_retrieved_docs(retrieved_docs)
        
        # Step 3: Build prompt for Claude
        full_prompt = self._build_prompt(user_query, context)
        
        # Step 4: Call Claude
        print("🤖 Generating response with Claude...")
        response = call_claude(full_prompt, max_tokens=max_tokens, temperature=temperature)
        
        # Step 5: Get metadata for references
        metadata = self.retriever.get_metadata_summary(retrieved_docs)
        
        return {
            "query": user_query,
            "response": response,
            "retrieved_documents": metadata,
            "num_documents": len(retrieved_docs)
        }
    
    def _build_prompt(self, user_query: str, context: str) -> str:
        """
        Build the full prompt for Claude.
        
        Args:
            user_query: User's question
            context: Retrieved document context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""{LEXIQ_SYSTEM_PROMPT}

RETRIEVED CASE LAW CONTEXT:
{context}

USER QUERY:
{user_query}

Please provide a comprehensive answer using the retrieved context above. Follow the markdown format specified in the rules."""
        
        return prompt
    
    def batch_query(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple queries in batch.
        
        Args:
            queries: List of user queries
            
        Returns:
            List of response dictionaries
        """
        if not self.is_initialized:
            raise ValueError("Query handler not initialized. Call initialize() first.")
        
        results = []
        for i, query in enumerate(queries, 1):
            print(f"\n--- Processing Query {i}/{len(queries)} ---")
            result = self.query(query)
            results.append(result)
        
        return results

