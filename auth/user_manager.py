#!/usr/bin/env python3
"""
User Manager
Simplified user management for development and Streamlit integration
"""

import bcrypt
import json
import os
from typing import Dict, Optional, Any
from pathlib import Path


class UserManager:
    """
    Simple user management system.
    Uses JSON file for development, can be replaced with database in production.
    """
    
    def __init__(self, users_file: str = "data/users.json"):
        """
        Initialize user manager.
        
        Args:
            users_file: Path to users JSON file
        """
        self.users_file = users_file
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file if it doesn't exist."""
        users_path = Path(self.users_file)
        users_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not users_path.exists():
            users_path.write_text(json.dumps({}))
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def register(self, 
                username: str,
                password: str,
                email: str,
                full_name: str = None,
                role: str = 'user') -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password (will be hashed)
            email: Email address
            full_name: Full name
            role: User role
            
        Returns:
            Registration result
        """
        users = self._load_users()
        
        # Check if username exists
        if username in users:
            return {
                'success': False,
                'error': 'Username already exists'
            }
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        users[username] = {
            'username': username,
            'password_hash': password_hash.decode('utf-8'),
            'email': email,
            'full_name': full_name or username,
            'role': role,
            'created_at': str(pd.Timestamp.now()) if 'pd' in dir() else None
        }
        
        self._save_users(users)
        
        return {
            'success': True,
            'username': username,
            'message': 'User registered successfully'
        }
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User info if authenticated, None otherwise
        """
        users = self._load_users()
        
        if username not in users:
            return None
        
        user = users[username]
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Return user info (without password hash)
            return {
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        
        return None
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information.
        
        Args:
            username: Username
            
        Returns:
            User info or None
        """
        users = self._load_users()
        
        if username in users:
            user = users[username].copy()
            user.pop('password_hash', None)  # Don't return password hash
            return user
        
        return None
    
    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """
        Update user information.
        
        Args:
            username: Username
            updates: Fields to update
            
        Returns:
            True if successful
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        # Don't allow password_hash update this way
        updates.pop('password_hash', None)
        
        users[username].update(updates)
        self._save_users(users)
        
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful
        """
        # Verify old password
        if not self.authenticate(username, old_password):
            return False
        
        users = self._load_users()
        
        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        users[username]['password_hash'] = password_hash.decode('utf-8')
        
        self._save_users(users)
        return True

