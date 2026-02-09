"""
Authentication Utilities for City Governance System
Password hashing, JWT token management, and OAuth helpers
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from urllib.parse import urlparse
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# Load configuration from environment
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

# Database connection parameters - parse from DATABASE_URL or individual vars
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    # Parse DATABASE_URL
    parsed = urlparse(DATABASE_URL)
    DB_CONFIG = {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "dbname": parsed.path[1:] if parsed.path else "city_mas",  # Remove leading /
        "user": parsed.username or "postgres",
        "password": parsed.password or "password"
    }
else:
    # Fall back to individual environment variables
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "city_mas"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password")
    }


# ==================== Database Connection ====================

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)


# ==================== Password Hashing ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


# ==================== JWT Token Management ====================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


# ==================== User Database Operations ====================

def create_user(email: str, password_hash: Optional[str], full_name: str, 
                role: str = "citizen", department: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Create a new user in database"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO users (email, password_hash, full_name, role, department, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, email, full_name, role, department, is_active, is_verified, created_at, last_login
                """, (email, password_hash, full_name, role, department, False))
                
                user = dict(cur.fetchone())
                conn.commit()
                return user
    except psycopg2.IntegrityError:
        logger.error(f"User with email {email} already exists")
        return None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, email, password_hash, full_name, role, department, 
                           is_active, is_verified, created_at, last_login
                    FROM users WHERE email = %s
                """, (email,))
                
                user = cur.fetchone()
                return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, email, password_hash, full_name, role, department, 
                           is_active, is_verified, created_at, last_login
                    FROM users WHERE id = %s
                """, (user_id,))
                
                user = cur.fetchone()
                return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None


def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (user_id,))
                conn.commit()
    except Exception as e:
        logger.error(f"Error updating last login: {e}")


# ==================== Session Management ====================

def create_session(user_id: int, access_token: str, refresh_token: str, 
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> bool:
    """Create a new session"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                
                cur.execute("""
                    INSERT INTO sessions (user_id, token, refresh_token, expires_at, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, access_token, refresh_token, expires_at, ip_address, user_agent))
                
                conn.commit()
                return True
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return False


def validate_session(token: str) -> Optional[Dict[str, Any]]:
    """Validate session token"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.*, u.email, u.role, u.department, u.is_active
                    FROM sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.token = %s AND s.expires_at > CURRENT_TIMESTAMP
                """, (token,))
                
                session = cur.fetchone()
                return dict(session) if session else None
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        return None


def delete_session(token: str) -> bool:
    """Delete a session (logout)"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
                conn.commit()
                return True
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        return False


# ==================== Google OAuth ====================

def verify_google_token(id_token_str: str) -> Optional[Dict[str, Any]]:
    """Verify Google ID token and extract user info"""
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            id_token_str, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Token is valid, extract user info
        return {
            "email": idinfo.get("email"),
            "full_name": idinfo.get("name"),
            "google_id": idinfo.get("sub"),
            "email_verified": idinfo.get("email_verified", False),
            "picture": idinfo.get("picture")
        }
    except ValueError as e:
        logger.error(f"Invalid Google token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        return None


def get_or_create_oauth_user(google_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get existing OAuth user or create new one"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if OAuth token exists
                cur.execute("""
                    SELECT u.* FROM users u
                    JOIN oauth_tokens ot ON u.id = ot.user_id
                    WHERE ot.provider = 'google' AND ot.provider_user_id = %s
                """, (google_info["google_id"],))
                
                user = cur.fetchone()
                
                if user:
                    # Update last login
                    update_last_login(user["id"])
                    return dict(user)
                
                # Check if user exists by email
                cur.execute("SELECT * FROM users WHERE email = %s", (google_info["email"],))
                user = cur.fetchone()
                
                if not user:
                    # Create new user (no password hash for OAuth users)
                    cur.execute("""
                        INSERT INTO users (email, full_name, role, is_verified, is_active)
                        VALUES (%s, %s, 'citizen', %s, TRUE)
                        RETURNING id, email, full_name, role, department, is_active, is_verified, created_at
                    """, (google_info["email"], google_info["full_name"], google_info.get("email_verified", False)))
                    
                    user = cur.fetchone()
                
                user_dict = dict(user)
                
                # Create OAuth token record
                cur.execute("""
                    INSERT INTO oauth_tokens (user_id, provider, provider_user_id)
                    VALUES (%s, 'google', %s)
                    ON CONFLICT (provider, provider_user_id) DO NOTHING
                """, (user_dict["id"], google_info["google_id"]))
                
                conn.commit()
                update_last_login(user_dict["id"])
                
                return user_dict
                
    except Exception as e:
        logger.error(f"Error getting/creating OAuth user: {e}")
        return None
