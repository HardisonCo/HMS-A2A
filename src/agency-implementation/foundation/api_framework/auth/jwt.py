"""
JWT authentication module for standardized API security.

This module provides JWT-based authentication functionality
that can be used consistently across all agency API implementations.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, Field


class TokenData(BaseModel):
    """
    Token data model for JWT payload validation.
    
    Attributes:
        username: Username of the authenticated user
        scopes: Optional list of permission scopes
        exp: Expiration timestamp
    """
    username: str
    scopes: list[str] = Field(default_factory=list)
    exp: Optional[datetime] = None


class JWTAuth:
    """
    JWT authentication handler for API security.
    
    This class provides methods for JWT token creation,
    validation, and user authentication.
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        token_url: str = "auth/token"
    ):
        """
        Initialize the JWT authentication handler.
        
        Args:
            secret_key: Secret key for signing JWT tokens
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Token expiration time in minutes
            token_url: Token endpoint URL
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a new JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        # Encode and sign JWT
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def decode_token(self, token: str) -> TokenData:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            TokenData object
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Decode JWT
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Extract username
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Extract scopes
            scopes = payload.get("scopes", [])
            
            # Extract expiration
            exp = payload.get("exp")
            if exp:
                exp = datetime.fromtimestamp(exp)
            
            # Create token data
            token_data = TokenData(username=username, scopes=scopes, exp=exp)
            
            return token_data
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_user(
        self,
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
        user_service: Any = None
    ) -> Any:
        """
        Get the current authenticated user.
        
        Args:
            token: JWT token
            user_service: Optional service for user data retrieval
            
        Returns:
            User object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        # Decode token
        token_data = self.decode_token(token)
        
        # If user service is provided, get user data
        if user_service:
            user = await user_service.get_by_username(token_data.username)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user
        
        # If no user service, return token data
        return token_data
    
    def has_required_scopes(self, required_scopes: list[str]) -> Any:
        """
        Check if user has required scopes.
        
        Args:
            required_scopes: List of required permission scopes
            
        Returns:
            Dependency function
        """
        async def _verify_scopes(user: TokenData = Depends(self.get_current_user)) -> TokenData:
            # Check if user has all required scopes
            user_scopes = set(user.scopes)
            missing_scopes = [scope for scope in required_scopes if scope not in user_scopes]
            
            if missing_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions. Missing scopes: {', '.join(missing_scopes)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user
        
        return _verify_scopes