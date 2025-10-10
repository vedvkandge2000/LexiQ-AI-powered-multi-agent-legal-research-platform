#!/usr/bin/env python3
"""
Conversation Engine
Chain-of-thought conversational interface with RAG integration
"""

from typing import Dict, List, Any, Optional
from aws.bedrock_client import BedrockClient
from utils.retriever import LegalDocumentRetriever
from utils.s3_pdf_reader import create_s3_pdf_reader


class ConversationEngine:
    """
    Conversational engine for discussing case analysis.
    Maintains context and uses RAG for informed responses.
    """
    
    def __init__(self, 
                 bedrock_client: BedrockClient = None,
                 retriever: LegalDocumentRetriever = None):
        """
        Initialize conversation engine.
        
        Args:
            bedrock_client: Bedrock client for Claude
            retriever: Legal document retriever for RAG
        """
        self.bedrock = bedrock_client or BedrockClient()
        self.retriever = retriever
        self.s3_pdf_reader = create_s3_pdf_reader()
    
    def generate_response(self,
                         user_message: str,
                         conversation_context: str = None,
                         initial_analysis: str = None,
                         retrieve_precedents: bool = True,
                         max_precedents: int = 3) -> Dict[str, Any]:
        """
        Generate conversational response with RAG context.
        
        Args:
            user_message: User's question/message
            conversation_context: Previous conversation history
            initial_analysis: Initial case analysis
            retrieve_precedents: Whether to retrieve relevant precedents
            max_precedents: Maximum precedents to retrieve
            
        Returns:
            Dictionary with response and metadata
        """
        # Retrieve relevant precedents if requested
        retrieved_docs = []
        if retrieve_precedents and self.retriever:
            try:
                docs = self.retriever.retrieve(user_message, k=max_precedents)
                retrieved_docs = []
                
                for doc in docs:
                    # Get basic metadata
                    doc_info = {
                        'case_title': doc.metadata.get('case_title', 'Unknown'),
                        'citation': doc.metadata.get('citation', 'N/A'),
                        'page_number': doc.metadata.get('page_number', 'N/A'),
                        's3_url': doc.metadata.get('s3_url', '') or doc.metadata.get('pdf_url', ''),
                        'content': doc.page_content[:500]  # Initial truncated content
                    }
                    
                    # Try to get full PDF content if S3 URL available
                    if doc_info['s3_url']:
                        try:
                            print(f"📄 Fetching full PDF content for {doc_info['case_title']}...")
                            full_content = self._get_full_pdf_content(
                                s3_url=doc_info['s3_url'],
                                page_number=doc_info['page_number']
                            )
                            if full_content:
                                doc_info['full_content'] = full_content
                                print(f"✅ Retrieved {len(full_content)} characters from PDF")
                            else:
                                print(f"⚠️ Could not retrieve full PDF content")
                        except Exception as e:
                            print(f"⚠️ Error fetching PDF content: {e}")
                    
                    retrieved_docs.append(doc_info)
                    
            except Exception as e:
                print(f"Warning: Could not retrieve precedents: {e}")
        
        # Build conversational prompt
        prompt = self._build_conversational_prompt(
            user_message=user_message,
            conversation_context=conversation_context,
            initial_analysis=initial_analysis,
            retrieved_docs=retrieved_docs
        )
        
        # Generate response using Claude
        try:
            response = self.bedrock.invoke_model(prompt, max_tokens=2000)
            
            return {
                'success': True,
                'response': response,
                'retrieved_precedents': len(retrieved_docs),
                'precedent_citations': [
                    f"{doc['case_title']} ({doc['citation']})" 
                    for doc in retrieved_docs
                ],
                'metadata': {
                    'model': 'claude-3-sonnet',
                    'context_used': bool(conversation_context or initial_analysis),
                    'rag_used': bool(retrieved_docs)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate response'
            }
    
    def _build_conversational_prompt(self,
                                    user_message: str,
                                    conversation_context: str = None,
                                    initial_analysis: str = None,
                                    retrieved_docs: List[Dict] = None) -> str:
        """
        Build prompt for conversational Claude interaction.
        
        Args:
            user_message: Current user message
            conversation_context: Previous conversation
            initial_analysis: Initial case analysis
            retrieved_docs: Retrieved precedent documents
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # System context
        prompt_parts.append("""You are a knowledgeable legal assistant helping discuss a legal case analysis. 
Your role is to:
- Answer questions about the case clearly and accurately
- Provide relevant legal insights based on precedents
- Clarify legal concepts in plain English
- Suggest additional angles to consider
- Maintain a professional but conversational tone

Be concise but thorough. Cite relevant precedents when applicable.""")
        
        # Initial analysis context
        if initial_analysis:
            prompt_parts.append(f"\n\nINITIAL CASE ANALYSIS:\n{initial_analysis}")
        
        # Retrieved precedents
        if retrieved_docs:
            prompt_parts.append("\n\nRELEVANT PRECEDENTS:")
            for i, doc in enumerate(retrieved_docs, 1):
                case_info = f"\n{i}. {doc['case_title']} ({doc['citation']})"
                case_info += f"\nPage: {doc.get('page_number', 'N/A')}"
                
                # Use full PDF content if available, otherwise use truncated content
                content = doc.get('full_content', doc.get('content', 'No content available'))
                if len(content) > 1000:
                    content = content[:1000] + "..."
                
                prompt_parts.append(f"{case_info}\nFull Text: {content}")
        
        # Conversation history
        if conversation_context:
            prompt_parts.append(f"\n\n{conversation_context}")
        
        # Current user message
        prompt_parts.append(f"\n\nUser: {user_message}")
        prompt_parts.append("\n\nAssistant: ")
        
        return "\n".join(prompt_parts)
    
    def generate_initial_analysis(self,
                                 case_text: str,
                                 similar_cases: List[Dict] = None) -> str:
        """
        Generate initial case analysis (for starting a conversation).
        
        Args:
            case_text: Case description/text
            similar_cases: Similar cases from RAG
            
        Returns:
            Initial analysis text
        """
        prompt = f"""Analyze the following legal case and provide a comprehensive initial assessment:

CASE TEXT:
{case_text}
"""
        
        if similar_cases:
            prompt += "\n\nRELEVANT PRECEDENTS:\n"
            for case in similar_cases[:5]:
                prompt += f"\n- {case.get('case_title', 'Unknown')} ({case.get('citation', 'N/A')})"
                prompt += f"\n  {case.get('content_preview', '')[:200]}...\n"
        
        prompt += """

Provide a structured analysis covering:
1. Key Legal Issues
2. Applicable Laws and Provisions
3. Relevant Precedents (if provided)
4. Potential Arguments
5. Likely Outcome
6. Key Considerations

Be thorough but concise. Format the analysis clearly."""
        
        try:
            analysis = self.bedrock.invoke_model(prompt, max_tokens=3000)
            return analysis
        except Exception as e:
            return f"Error generating analysis: {str(e)}"
    
    def generate_followup_questions(self,
                                   conversation_context: str,
                                   last_response: str) -> List[str]:
        """
        Generate suggested follow-up questions based on conversation.
        
        Args:
            conversation_context: Full conversation history
            last_response: Last assistant response
            
        Returns:
            List of suggested questions
        """
        prompt = f"""Based on this legal discussion, suggest 3 relevant follow-up questions the user might want to ask:

LAST RESPONSE:
{last_response}

Generate 3 specific, relevant questions that would help deepen the legal analysis. 
Format as a simple numbered list."""
        
        try:
            response = self.bedrock.invoke_model(prompt, max_tokens=300)
            
            # Parse questions from response
            questions = []
            for line in response.split('\n'):
                line = line.strip()
                # Match numbered list items
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    question = line.lstrip('0123456789.-•) ').strip()
                    if question and len(question) > 10:
                        questions.append(question)
            
            return questions[:3]
            
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return []
    
    def summarize_conversation(self, 
                              conversation_context: str,
                              initial_analysis: str = None) -> str:
        """
        Generate a summary of the conversation.
        
        Args:
            conversation_context: Full conversation history
            initial_analysis: Initial analysis if available
            
        Returns:
            Conversation summary
        """
        prompt = f"""Summarize this legal case discussion, highlighting key points discussed and conclusions reached:

"""
        
        if initial_analysis:
            prompt += f"INITIAL ANALYSIS:\n{initial_analysis}\n\n"
        
        prompt += f"""CONVERSATION:
{conversation_context}

Provide a concise summary covering:
1. Main legal issues discussed
2. Key precedents referenced
3. Important conclusions or insights
4. Remaining questions or areas for further exploration"""
        
        try:
            summary = self.bedrock.invoke_model(prompt, max_tokens=1000)
            return summary
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _get_full_pdf_content(self, s3_url: str, page_number) -> Optional[str]:
        """
        Get full PDF content from S3.
        
        Args:
            s3_url: S3 URL of the PDF
            page_number: Page number as string or int
            
        Returns:
            Full PDF content or None if failed
        """
        try:
            # Convert page number to int
            if isinstance(page_number, str):
                page_num = int(page_number) if page_number.isdigit() else 1
            elif isinstance(page_number, int):
                page_num = page_number
            else:
                page_num = 1
            
            # Extract page content
            content = self.s3_pdf_reader.extract_page_content(s3_url, page_num)
            return content
            
        except Exception as e:
            print(f"Error getting PDF content: {e}")
            return None

