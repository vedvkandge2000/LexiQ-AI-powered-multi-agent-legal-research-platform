#!/usr/bin/env python3
"""
Chat Storage with DynamoDB
Persists chat history, sessions, and conversation context
"""

import boto3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal
from botocore.exceptions import ClientError


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder for Decimal types from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class ChatStorage:
    """
    DynamoDB-based storage for chat sessions and messages.
    Falls back to in-memory storage if DynamoDB is not configured.
    """
    
    def __init__(self, 
                 table_name: Optional[str] = None,
                 region: str = 'us-east-1'):
        """
        Initialize chat storage.
        
        Args:
            table_name: DynamoDB table name (from env if not provided)
            region: AWS region
        """
        self.table_name = table_name or os.environ.get('DYNAMODB_CHAT_TABLE', 'lexiq-chat-history')
        self.region = region
        
        try:
            # Initialize DynamoDB
            dynamodb = boto3.resource('dynamodb', region_name=region)
            self.table = dynamodb.Table(self.table_name)
            
            # Test connection
            self.table.table_status
            self.mock_mode = False
            print(f"✓ Connected to DynamoDB table: {self.table_name}")
            
        except Exception as e:
            print(f"⚠️  DynamoDB not available: {e}")
            print("Using in-memory storage (data will not persist)")
            self.mock_mode = True
            self._mock_storage = {}  # In-memory fallback
    
    def create_session(self, 
                      user_id: str,
                      case_title: str = None,
                      initial_analysis: str = None) -> str:
        """
        Create a new chat session.
        
        Args:
            user_id: User ID
            case_title: Title/description of the case
            initial_analysis: Initial case analysis from RAG
            
        Returns:
            Session ID
        """
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'case_title': case_title or 'Untitled Case',
            'initial_analysis': initial_analysis or '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'message_count': 0,
            'status': 'active'
        }
        
        if self.mock_mode:
            self._mock_storage[session_id] = {
                'session': session_data,
                'messages': []
            }
        else:
            try:
                self.table.put_item(Item=session_data)
            except ClientError as e:
                print(f"Error creating session: {e}")
                return None
        
        return session_id
    
    def add_message(self,
                   session_id: str,
                   role: str,
                   content: str,
                   metadata: Dict[str, Any] = None) -> bool:
        """
        Add a message to a chat session.
        
        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Additional metadata (e.g., retrieved docs, confidence)
            
        Returns:
            True if successful
        """
        message = {
            'session_id': session_id,
            'message_id': f"{session_id}_{int(datetime.now().timestamp() * 1000)}",
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        if self.mock_mode:
            if session_id not in self._mock_storage:
                return False
            self._mock_storage[session_id]['messages'].append(message)
            self._mock_storage[session_id]['session']['message_count'] += 1
            self._mock_storage[session_id]['session']['updated_at'] = datetime.now().isoformat()
            return True
        
        try:
            # Add message
            self.table.put_item(Item=message)
            
            # Update session
            self.table.update_item(
                Key={'session_id': session_id},
                UpdateExpression='SET message_count = message_count + :inc, updated_at = :timestamp',
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':timestamp': datetime.now().isoformat()
                }
            )
            return True
            
        except ClientError as e:
            print(f"Error adding message: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session dictionary or None
        """
        if self.mock_mode:
            if session_id in self._mock_storage:
                return self._mock_storage[session_id]['session']
            return None
        
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            return response.get('Item')
        except ClientError:
            return None
    
    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        if self.mock_mode:
            if session_id in self._mock_storage:
                messages = self._mock_storage[session_id]['messages']
                return sorted(messages, key=lambda x: x['timestamp'])[-limit:]
            return []
        
        try:
            response = self.table.query(
                IndexName='session-messages-index',  # Requires GSI
                KeyConditionExpression='session_id = :sid',
                ExpressionAttributeValues={':sid': session_id},
                Limit=limit,
                ScanIndexForward=True  # Oldest first
            )
            return response.get('Items', [])
        except ClientError:
            # Fallback if GSI not configured
            return []
    
    def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions
            
        Returns:
            List of sessions
        """
        if self.mock_mode:
            sessions = [
                data['session'] 
                for data in self._mock_storage.values()
                if data['session']['user_id'] == user_id
            ]
            return sorted(sessions, key=lambda x: x['updated_at'], reverse=True)[:limit]
        
        try:
            response = self.table.query(
                IndexName='user-sessions-index',  # Requires GSI
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                Limit=limit,
                ScanIndexForward=False  # Newest first
            )
            return response.get('Items', [])
        except ClientError:
            return []
    
    def update_session(self, 
                      session_id: str,
                      updates: Dict[str, Any]) -> bool:
        """
        Update session metadata.
        
        Args:
            session_id: Session ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        if self.mock_mode:
            if session_id in self._mock_storage:
                self._mock_storage[session_id]['session'].update(updates)
                self._mock_storage[session_id]['session']['updated_at'] = datetime.now().isoformat()
                return True
            return False
        
        try:
            # Build update expression
            update_expr = 'SET '
            expr_values = {}
            
            for i, (key, value) in enumerate(updates.items()):
                update_expr += f"{key} = :{key}"
                if i < len(updates) - 1:
                    update_expr += ', '
                expr_values[f':{key}'] = value
            
            update_expr += ', updated_at = :timestamp'
            expr_values[':timestamp'] = datetime.now().isoformat()
            
            self.table.update_item(
                Key={'session_id': session_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values
            )
            return True
            
        except ClientError:
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session and all its messages.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        if self.mock_mode:
            if session_id in self._mock_storage:
                del self._mock_storage[session_id]
                return True
            return False
        
        try:
            # Delete session
            self.table.delete_item(Key={'session_id': session_id})
            
            # Delete all messages (would need batch delete in production)
            messages = self.get_messages(session_id)
            for msg in messages:
                self.table.delete_item(Key={'message_id': msg['message_id']})
            
            return True
            
        except ClientError:
            return False
    
    def get_conversation_context(self, 
                                session_id: str,
                                max_messages: int = 10) -> str:
        """
        Get conversation context as formatted string for LLM.
        
        Args:
            session_id: Session ID
            max_messages: Maximum recent messages to include
            
        Returns:
            Formatted conversation history
        """
        session = self.get_session(session_id)
        messages = self.get_messages(session_id, limit=max_messages)
        
        context = []
        
        # Add initial analysis if available
        if session and session.get('initial_analysis'):
            context.append(f"INITIAL CASE ANALYSIS:\n{session['initial_analysis']}\n")
        
        # Add conversation history
        if messages:
            context.append("CONVERSATION HISTORY:")
            for msg in messages:
                role_label = "User" if msg['role'] == 'user' else "Assistant"
                context.append(f"{role_label}: {msg['content']}")
        
        return "\n\n".join(context)

