"""
Authentication Routes for City Governance System
FastAPI endpoints for user registration, login, logout, and OAuth
"""

from fastapi import APIRouter, HTTPException, Header, Request, status
from typing import Optional
import logging

from ..auth_schemas import (
    UserRegister, UserLogin, TokenRefresh, GoogleAuthRequest,
    AuthResponse, UserResponse, Token, MessageResponse
)
from ..auth_utils import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, create_user, get_user_by_email, get_user_by_id,
    update_last_login, create_session, validate_session, delete_session,
    verify_google_token, get_or_create_oauth_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


# ==================== Helper Functions ====================

def get_client_info(request: Request):
    """Extract client IP and user agent"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }


def create_auth_response(user: dict, request: Request) -> AuthResponse:
    """Create authentication response with tokens"""
    # Create tokens
    access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["email"], "user_id": user["id"]})
    
    # Create session
    client_info = get_client_info(request)
    create_session(
        user_id=user["id"],
        access_token=access_token,
        refresh_token=refresh_token,
        **client_info
    )
    
    # Update last login
    update_last_login(user["id"])
    
    # Build response
    return AuthResponse(
        user=UserResponse(**user),
        token=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


# ==================== Authentication Routes ====================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, request: Request):
    """
    Register a new user with email and password
    
    - **email**: Valid email address
    - **password**: Min 8 chars, must contain uppercase, lowercase, and digit
    - **full_name**: User's full name
    - **role**: Optional role (default: citizen)
    - **department**: Optional department (for department users)
    """
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    user = create_user(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        role=user_data.role.value if user_data.role else "citizen",
        department=user_data.department.value if user_data.department else None
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    logger.info(f"User registered successfully: {user['email']}")
    
    # Return authentication response with tokens
    return create_auth_response(user, request)


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, request: Request):
    """
    Login with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token and refresh token
    """
    logger.info(f"Login attempt for email: {credentials.email}")
    
    # Get user
    user = get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact administrator."
        )
    
    # Verify password
    if not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses OAuth login. Please login with Google."
        )
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info(f"User logged in successfully: {user['email']}")
    
    # Return authentication response with tokens
    return create_auth_response(user, request)


@router.post("/google", response_model=AuthResponse)
async def google_login(google_data: GoogleAuthRequest, request: Request):
    """
    Login or register with Google OAuth
    
    - **id_token**: Google ID token from frontend
    
    Returns access token and refresh token
    """
    logger.info("Google OAuth login attempt")
    
    # Verify Google token
    google_info = verify_google_token(google_data.id_token)
    if not google_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    logger.info(f"Google token verified for: {google_info['email']}")
    
    # Get or create user
    user = get_or_create_oauth_user(google_info)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate with Google"
        )
    
    # Check if user is active
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact administrator."
        )
    
    logger.info(f"Google OAuth successful: {user['email']}")
    
    # Return authentication response with tokens
    return create_auth_response(user, request)


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token
    """
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    user_id = payload.get("user_id")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
    refresh_token_new = create_refresh_token(data={"sub": user["email"], "user_id": user["id"]})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token_new,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout and invalidate session
    
    - **Authorization**: Bearer token in header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    # Delete session
    success = delete_session(token)
    if not success:
        logger.warning("Failed to delete session during logout")
    
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Get current authenticated user information
    
    - **Authorization**: Bearer token in header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    # Validate session
    session = validate_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user
    user = get_user_by_id(session["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)


@router.get("/verify", response_model=MessageResponse)
async def verify_token_endpoint(authorization: Optional[str] = Header(None)):
    """
    Verify if a token is valid
    
    - **Authorization**: Bearer token in header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    # Validate session
    session = validate_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return MessageResponse(message="Token is valid", success=True)
