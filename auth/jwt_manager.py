#!/usr/bin/env python3
"""
JWT Token Manager
Handles JWT token creation, validation, and management for API authentication
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps
from flask import request, jsonify


class JWTManager:
    """
    JWT token manager for API authentication.
    Works with Cognito tokens or custom JWT tokens.
    """
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = 'HS256'):
        """
        Initialize JWT manager.
        
        Args:
            secret_key: Secret key for signing tokens (from env if not provided)
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
        self.algorithm = algorithm
        self.token_expiry = 3600  # 1 hour
        self.refresh_token_expiry = 86400 * 30  # 30 days
    
    def create_access_token(self, user_id: str, username: str, role: str = 'user') -> str:
        """
        Create JWT access token.
        
        Args:
            user_id: User ID
            username: Username
            role: User role
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str, username: str) -> str:
        """
        Create JWT refresh token.
        
        Args:
            user_id: User ID
            username: Username
            
        Returns:
            JWT refresh token string
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(seconds=self.refresh_token_expiry),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    def verify_token(self, token: str) -> bool:
        """
        Verify if token is valid.
        
        Args:
            token: JWT token string
            
        Returns:
            True if valid, False otherwise
        """
        return self.decode_token(token) is not None
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user information from token.
        
        Args:
            token: JWT token string
            
        Returns:
            User info dictionary or None
        """
        payload = self.decode_token(token)
        if payload:
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'role': payload.get('role', 'user')
            }
        return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            New access token or None if invalid
        """
        payload = self.decode_token(refresh_token)
        
        if payload and payload.get('type') == 'refresh':
            return self.create_access_token(
                user_id=payload['user_id'],
                username=payload['username'],
                role=payload.get('role', 'user')
            )
        
        return None
    
    # Flask decorators for API protection
    def token_required(self, f):
        """
        Decorator to protect Flask routes with JWT authentication.
        
        Usage:
            @app.route('/protected')
            @jwt_manager.token_required
            def protected_route(current_user):
                return jsonify({'user': current_user})
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            # Get token from header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    return jsonify({'error': 'Invalid token format'}), 401
            
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
            
            # Verify token
            current_user = self.get_user_from_token(token)
            
            if not current_user:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            return f(current_user, *args, **kwargs)
        
        return decorated
    
    def role_required(self, allowed_roles: list):
        """
        Decorator to restrict access based on user role.
        
        Usage:
            @app.route('/admin')
            @jwt_manager.role_required(['admin'])
            def admin_route(current_user):
                return jsonify({'admin': True})
        """
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = None
                
                if 'Authorization' in request.headers:
                    auth_header = request.headers['Authorization']
                    try:
                        token = auth_header.split(' ')[1]
                    except IndexError:
                        return jsonify({'error': 'Invalid token format'}), 401
                
                if not token:
                    return jsonify({'error': 'Token is missing'}), 401
                
                current_user = self.get_user_from_token(token)
                
                if not current_user:
                    return jsonify({'error': 'Token is invalid or expired'}), 401
                
                if current_user['role'] not in allowed_roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(current_user, *args, **kwargs)
            
            return decorated
        return decorator

