#!/usr/bin/env python3
"""
Chat Manager
Orchestrates chat sessions, storage, and conversation engine
"""

from typing import Dict, List, Any, Optional
from .chat_storage import ChatStorage
from .conversation_engine import ConversationEngine
from aws.bedrock_client import BedrockClient
from utils.retriever import LegalDocumentRetriever


class ChatManager:
    """
    High-level chat manager.
    Handles session management, message flow, and coordinates storage + engine.
    """
    
    def __init__(self,
                 bedrock_client: BedrockClient = None,
                 retriever: LegalDocumentRetriever = None,
                 storage: ChatStorage = None):
        """
        Initialize chat manager.
        
        Args:
            bedrock_client: Bedrock client for Claude
            retriever: Legal document retriever
            storage: Chat storage (DynamoDB or in-memory)
        """
        self.storage = storage or ChatStorage()
        self.engine = ConversationEngine(
            bedrock_client=bedrock_client or BedrockClient(),
            retriever=retriever
        )
    
    def start_new_chat(self,
                      user_id: str,
                      case_text: str = None,
                      case_title: str = None,
                      similar_cases: List[Dict] = None) -> Dict[str, Any]:
        """
        Start a new chat session with initial analysis.
        
        Args:
            user_id: User ID
            case_text: Case text for analysis
            case_title: Title for the chat session
            similar_cases: Pre-retrieved similar cases
            
        Returns:
            Dictionary with session info and initial analysis
        """
        # Generate initial analysis if case text provided
        initial_analysis = None
        if case_text:
            initial_analysis = self.engine.generate_initial_analysis(
                case_text=case_text,
                similar_cases=similar_cases
            )
        
        # Create session
        session_id = self.storage.create_session(
            user_id=user_id,
            case_title=case_title or 'New Case Discussion',
            initial_analysis=initial_analysis
        )
        
        if not session_id:
            return {
                'success': False,
                'error': 'Failed to create chat session'
            }
        
        # Add initial analysis as first message
        if initial_analysis:
            self.storage.add_message(
                session_id=session_id,
                role='assistant',
                content=initial_analysis,
                metadata={'type': 'initial_analysis'}
            )
        
        return {
            'success': True,
            'session_id': session_id,
            'initial_analysis': initial_analysis,
            'message': 'Chat session started. You can now ask questions about the case.'
        }
    
    def send_message(self,
                    session_id: str,
                    user_message: str,
                    use_rag: bool = True) -> Dict[str, Any]:
        """
        Send a user message and get response.
        
        Args:
            session_id: Chat session ID
            user_message: User's message
            use_rag: Whether to use RAG for precedent retrieval
            
        Returns:
            Dictionary with assistant response
        """
        # Verify session exists
        session = self.storage.get_session(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        # Store user message
        self.storage.add_message(
            session_id=session_id,
            role='user',
            content=user_message
        )
        
        # Get conversation context
        context = self.storage.get_conversation_context(session_id, max_messages=10)
        
        # Generate response
        result = self.engine.generate_response(
            user_message=user_message,
            conversation_context=context,
            initial_analysis=session.get('initial_analysis'),
            retrieve_precedents=use_rag
        )
        
        if not result['success']:
            return result
        
        # Store assistant response
        self.storage.add_message(
            session_id=session_id,
            role='assistant',
            content=result['response'],
            metadata={
                'precedents_used': result['retrieved_precedents'],
                'citations': result['precedent_citations']
            }
        )
        
        # Generate follow-up questions
        followup_questions = self.engine.generate_followup_questions(
            conversation_context=context,
            last_response=result['response']
        )
        
        return {
            'success': True,
            'response': result['response'],
            'precedents_used': result.get('precedents_used', []),
            'num_precedents': result.get('num_precedents', 0),
            'precedent_citations': result.get('precedent_citations', []),
            'suggested_questions': followup_questions,
            'metadata': result.get('metadata', {})
        }
    
    def get_chat_history(self, 
                        session_id: str,
                        limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get full chat history for a session.
        
        Args:
            session_id: Chat session ID
            limit: Maximum messages to retrieve
            
        Returns:
            List of messages
        """
        return self.storage.get_messages(session_id, limit=limit)
    
    def get_user_chats(self, 
                      user_id: str,
                      limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum sessions to retrieve
            
        Returns:
            List of chat sessions
        """
        return self.storage.get_user_sessions(user_id, limit=limit)
    
    def rename_chat(self, 
                   session_id: str,
                   new_title: str) -> bool:
        """
        Rename a chat session.
        
        Args:
            session_id: Chat session ID
            new_title: New title
            
        Returns:
            True if successful
        """
        return self.storage.update_session(
            session_id=session_id,
            updates={'case_title': new_title}
        )
    
    def delete_chat(self, session_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: Chat session ID
            
        Returns:
            True if successful
        """
        return self.storage.delete_session(session_id)
    
    def summarize_chat(self, session_id: str) -> Optional[str]:
        """
        Generate a summary of the chat session.
        
        Args:
            session_id: Chat session ID
            
        Returns:
            Summary text or None
        """
        session = self.storage.get_session(session_id)
        if not session:
            return None
        
        context = self.storage.get_conversation_context(session_id)
        
        return self.engine.summarize_conversation(
            conversation_context=context,
            initial_analysis=session.get('initial_analysis')
        )
    
    def export_chat(self, 
                   session_id: str,
                   format: str = 'markdown') -> Optional[str]:
        """
        Export chat session to text format.
        
        Args:
            session_id: Chat session ID
            format: Export format ('markdown' or 'plain')
            
        Returns:
            Formatted chat export or None
        """
        session = self.storage.get_session(session_id)
        messages = self.storage.get_messages(session_id)
        
        if not session or not messages:
            return None
        
        if format == 'markdown':
            return self._export_as_markdown(session, messages)
        else:
            return self._export_as_plain_text(session, messages)
    
    def _export_as_markdown(self, 
                           session: Dict,
                           messages: List[Dict]) -> str:
        """Export chat as Markdown."""
        lines = []
        lines.append(f"# {session['case_title']}")
        lines.append(f"\n**Date:** {session['created_at']}")
        lines.append(f"**Session ID:** {session['session_id']}\n")
        lines.append("---\n")
        
        for msg in messages:
            role = "👤 **User**" if msg['role'] == 'user' else "🤖 **Assistant**"
            lines.append(f"## {role}\n")
            lines.append(f"{msg['content']}\n")
            
            # Add precedent citations if available
            if msg['role'] == 'assistant' and msg.get('metadata', {}).get('citations'):
                lines.append("\n*Referenced Precedents:*")
                for cite in msg['metadata']['citations']:
                    lines.append(f"- {cite}")
                lines.append("")
            
            lines.append("---\n")
        
        return "\n".join(lines)
    
    def _export_as_plain_text(self,
                             session: Dict,
                             messages: List[Dict]) -> str:
        """Export chat as plain text."""
        lines = []
        lines.append(f"Case: {session['case_title']}")
        lines.append(f"Date: {session['created_at']}")
        lines.append(f"Session: {session['session_id']}")
        lines.append("\n" + "="*80 + "\n")
        
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            lines.append(f"{role}:")
            lines.append(f"{msg['content']}\n")
            lines.append("-"*80 + "\n")
        
        return "\n".join(lines)

