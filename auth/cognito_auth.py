#!/usr/bin/env python3
"""
AWS Cognito Authentication
Handles user registration, login, and session management using AWS Cognito
"""

import boto3
import hmac
import hashlib
import base64
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
import os


class CognitoAuth:
    """
    AWS Cognito authentication handler.
    Manages user registration, login, password management, and MFA.
    """
    
    def __init__(self, 
                 user_pool_id: Optional[str] = None,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 region: str = 'us-east-1'):
        """
        Initialize Cognito authentication.
        
        Args:
            user_pool_id: Cognito User Pool ID (from env if not provided)
            client_id: Cognito App Client ID (from env if not provided)
            client_secret: Cognito App Client Secret (from env if not provided)
            region: AWS region
        """
        self.user_pool_id = user_pool_id or os.environ.get('COGNITO_USER_POOL_ID')
        self.client_id = client_id or os.environ.get('COGNITO_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('COGNITO_CLIENT_SECRET')
        self.region = region
        
        # Initialize Cognito client
        self.client = boto3.client('cognito-idp', region_name=region)
        
        # Check if credentials are set
        if not self.user_pool_id or not self.client_id:
            print("Warning: Cognito credentials not fully configured. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    def _get_secret_hash(self, username: str) -> str:
        """
        Calculate secret hash for Cognito authentication.
        
        Args:
            username: User's username
            
        Returns:
            Base64 encoded secret hash
        """
        if not self.client_secret:
            return None
            
        message = username + self.client_id
        dig = hmac.new(
            self.client_secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()
    
    def register_user(self, 
                     username: str,
                     password: str,
                     email: str,
                     full_name: str = None,
                     role: str = 'user') -> Dict[str, Any]:
        """
        Register a new user in Cognito.
        
        Args:
            username: Username (must be unique)
            password: Password (must meet Cognito password policy)
            email: Email address
            full_name: User's full name
            role: User role (user, lawyer, admin)
            
        Returns:
            Dictionary with registration result
        """
        if self.mock_mode:
            return self._mock_register(username, email, role)
        
        try:
            # Prepare user attributes
            user_attributes = [
                {'Name': 'email', 'Value': email},
                {'Name': 'custom:role', 'Value': role}
            ]
            
            if full_name:
                user_attributes.append({'Name': 'name', 'Value': full_name})
            
            # Prepare request parameters
            params = {
                'ClientId': self.client_id,
                'Username': username,
                'Password': password,
                'UserAttributes': user_attributes
            }
            
            # Add secret hash if available
            if self.client_secret:
                params['SecretHash'] = self._get_secret_hash(username)
            
            # Register user
            response = self.client.sign_up(**params)
            
            return {
                'success': True,
                'user_sub': response['UserSub'],
                'username': username,
                'email': email,
                'role': role,
                'confirmation_required': not response.get('UserConfirmed', False),
                'message': 'User registered successfully. Please check email for verification code.'
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            return {
                'success': False,
                'error': error_code,
                'message': self._get_friendly_error_message(error_code, error_message)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'UnknownError',
                'message': f'Registration failed: {str(e)}'
            }
    
    def confirm_registration(self, username: str, confirmation_code: str) -> Dict[str, Any]:
        """
        Confirm user registration with verification code.
        
        Args:
            username: Username
            confirmation_code: Code sent to user's email
            
        Returns:
            Dictionary with confirmation result
        """
        if self.mock_mode:
            return {'success': True, 'message': 'User confirmed (mock mode)'}
        
        try:
            params = {
                'ClientId': self.client_id,
                'Username': username,
                'ConfirmationCode': confirmation_code
            }
            
            if self.client_secret:
                params['SecretHash'] = self._get_secret_hash(username)
            
            self.client.confirm_sign_up(**params)
            
            return {
                'success': True,
                'message': 'Email confirmed successfully. You can now log in.'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Code'],
                'message': self._get_friendly_error_message(
                    e.response['Error']['Code'],
                    e.response['Error']['Message']
                )
            }
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and get tokens.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Dictionary with authentication tokens and user info
        """
        if self.mock_mode:
            return self._mock_login(username)
        
        try:
            params = {
                'ClientId': self.client_id,
                'AuthFlow': 'USER_PASSWORD_AUTH',
                'AuthParameters': {
                    'USERNAME': username,
                    'PASSWORD': password
                }
            }
            
            if self.client_secret:
                params['AuthParameters']['SECRET_HASH'] = self._get_secret_hash(username)
            
            response = self.client.initiate_auth(**params)
            
            # Extract tokens
            auth_result = response['AuthenticationResult']
            
            # Get user attributes
            user_info = self.get_user_info(auth_result['AccessToken'])
            
            return {
                'success': True,
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'refresh_token': auth_result['RefreshToken'],
                'expires_in': auth_result['ExpiresIn'],
                'token_type': auth_result['TokenType'],
                'user_info': user_info
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            return {
                'success': False,
                'error': error_code,
                'message': self._get_friendly_error_message(
                    error_code,
                    e.response['Error']['Message']
                )
            }
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from access token.
        
        Args:
            access_token: Cognito access token
            
        Returns:
            Dictionary with user attributes
        """
        if self.mock_mode:
            return {'username': 'test_user', 'email': 'test@example.com', 'role': 'user'}
        
        try:
            response = self.client.get_user(AccessToken=access_token)
            
            # Parse user attributes
            user_data = {'username': response['Username']}
            for attr in response['UserAttributes']:
                user_data[attr['Name']] = attr['Value']
            
            return user_data
            
        except ClientError:
            return None
    
    def refresh_token(self, refresh_token: str, username: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Cognito refresh token
            username: Username
            
        Returns:
            Dictionary with new tokens
        """
        if self.mock_mode:
            return {'success': True, 'access_token': 'mock_token', 'expires_in': 3600}
        
        try:
            params = {
                'ClientId': self.client_id,
                'AuthFlow': 'REFRESH_TOKEN_AUTH',
                'AuthParameters': {
                    'REFRESH_TOKEN': refresh_token
                }
            }
            
            if self.client_secret:
                params['AuthParameters']['SECRET_HASH'] = self._get_secret_hash(username)
            
            response = self.client.initiate_auth(**params)
            auth_result = response['AuthenticationResult']
            
            return {
                'success': True,
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'expires_in': auth_result['ExpiresIn']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Code'],
                'message': 'Token refresh failed'
            }
    
    def logout(self, access_token: str) -> Dict[str, Any]:
        """
        Sign out user (invalidate tokens).
        
        Args:
            access_token: User's access token
            
        Returns:
            Dictionary with logout result
        """
        if self.mock_mode:
            return {'success': True, 'message': 'Logged out (mock mode)'}
        
        try:
            self.client.global_sign_out(AccessToken=access_token)
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
        except ClientError:
            return {
                'success': False,
                'message': 'Logout failed'
            }
    
    def change_password(self, 
                       access_token: str,
                       old_password: str,
                       new_password: str) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            access_token: User's access token
            old_password: Current password
            new_password: New password
            
        Returns:
            Dictionary with result
        """
        if self.mock_mode:
            return {'success': True, 'message': 'Password changed (mock mode)'}
        
        try:
            self.client.change_password(
                AccessToken=access_token,
                PreviousPassword=old_password,
                ProposedPassword=new_password
            )
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Code'],
                'message': 'Password change failed'
            }
    
    def forgot_password(self, username: str) -> Dict[str, Any]:
        """
        Initiate forgot password flow.
        
        Args:
            username: Username
            
        Returns:
            Dictionary with result
        """
        if self.mock_mode:
            return {'success': True, 'message': 'Password reset code sent (mock mode)'}
        
        try:
            params = {
                'ClientId': self.client_id,
                'Username': username
            }
            
            if self.client_secret:
                params['SecretHash'] = self._get_secret_hash(username)
            
            self.client.forgot_password(**params)
            return {
                'success': True,
                'message': 'Password reset code sent to your email'
            }
        except ClientError as e:
            return {
                'success': False,
                'message': 'Password reset request failed'
            }
    
    def confirm_forgot_password(self,
                               username: str,
                               confirmation_code: str,
                               new_password: str) -> Dict[str, Any]:
        """
        Confirm forgot password with code and set new password.
        
        Args:
            username: Username
            confirmation_code: Code from email
            new_password: New password
            
        Returns:
            Dictionary with result
        """
        if self.mock_mode:
            return {'success': True, 'message': 'Password reset (mock mode)'}
        
        try:
            params = {
                'ClientId': self.client_id,
                'Username': username,
                'ConfirmationCode': confirmation_code,
                'Password': new_password
            }
            
            if self.client_secret:
                params['SecretHash'] = self._get_secret_hash(username)
            
            self.client.confirm_forgot_password(**params)
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
        except ClientError as e:
            return {
                'success': False,
                'message': 'Password reset confirmation failed'
            }
    
    def _get_friendly_error_message(self, error_code: str, original_message: str) -> str:
        """Convert AWS error codes to user-friendly messages."""
        error_messages = {
            'UsernameExistsException': 'Username already exists. Please choose a different username.',
            'InvalidPasswordException': 'Password does not meet requirements. Must be at least 8 characters with uppercase, lowercase, number, and special character.',
            'InvalidParameterException': 'Invalid input. Please check your information and try again.',
            'NotAuthorizedException': 'Incorrect username or password.',
            'UserNotFoundException': 'User not found.',
            'CodeMismatchException': 'Invalid verification code.',
            'ExpiredCodeException': 'Verification code expired. Please request a new one.',
            'UserNotConfirmedException': 'Please verify your email before logging in.',
            'TooManyRequestsException': 'Too many attempts. Please try again later.',
            'LimitExceededException': 'Limit exceeded. Please try again later.'
        }
        
        return error_messages.get(error_code, original_message)
    
    # Mock methods for development without AWS Cognito
    def _mock_register(self, username: str, email: str, role: str) -> Dict[str, Any]:
        """Mock registration for development."""
        return {
            'success': True,
            'user_sub': f'mock-{username}',
            'username': username,
            'email': email,
            'role': role,
            'confirmation_required': False,
            'message': 'User registered successfully (mock mode - no Cognito configured)'
        }
    
    def _mock_login(self, username: str) -> Dict[str, Any]:
        """Mock login for development."""
        return {
            'success': True,
            'access_token': f'mock_access_token_{username}',
            'id_token': f'mock_id_token_{username}',
            'refresh_token': f'mock_refresh_token_{username}',
            'expires_in': 3600,
            'token_type': 'Bearer',
            'user_info': {
                'username': username,
                'email': f'{username}@example.com',
                'role': 'user'
            }
        }

