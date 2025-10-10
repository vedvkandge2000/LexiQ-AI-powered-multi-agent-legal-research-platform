"""
LexiQ Authentication Module
AWS Cognito-based authentication with JWT tokens
"""

from .cognito_auth import CognitoAuth
from .jwt_manager import JWTManager
from .user_manager import UserManager

__all__ = ['CognitoAuth', 'JWTManager', 'UserManager']

