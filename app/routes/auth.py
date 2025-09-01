"""
Authentication routes for Supabase Auth integration
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging
import json
import httpx
import os
from datetime import datetime

from ..services.supabase_auth import SupabaseAuthService
from ..models import User
from ..schemas import (
    AuthRequest, 
    AuthSignUpRequest, 
    OAuthRequest, 
    AuthResponse,
    TokenVerificationRequest,
    TokenVerificationResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    APIResponse
)
from ..database import get_async_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])

async def get_auth_service():
    """Dependency to get Supabase auth service"""
    return SupabaseAuthService()

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Get current user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify token with Supabase
        token_data = await auth_service.verify_token(token)
        if not token_data:
            return None
        
        # Get user from database
        user_id = token_data.get("sub")
        if not user_id:
            return None
        
        result = await db.execute(
            select(User).where(User.supabase_user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return None

@router.post("/signup", response_model=AuthResponse)
async def sign_up(
    auth_request: AuthSignUpRequest,
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign up a new user with full profile data"""
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == auth_request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Sign up with Supabase Auth
        auth_response = await auth_service.sign_up_with_email(
            email=auth_request.email,
            password=auth_request.password,
            user_data={
                "name": auth_request.name,
                "age": auth_request.age,
                "weight": auth_request.weight,
                "height": auth_request.height,
                "fitness_goals": auth_request.fitness_goals,
                "fitness_goal_type": auth_request.fitness_goal_type,
                "injuries_limitations": auth_request.injuries_limitations
            }
        )
        
        # Check if auth_response is None
        if auth_response is None:
            logger.error("Auth service returned None response")
            raise HTTPException(status_code=500, detail="Authentication service error")
        
        # Validate auth_response structure
        if not hasattr(auth_response, 'user') or not hasattr(auth_response, 'session'):
            logger.error(f"Invalid auth response structure: {auth_response}")
            raise HTTPException(status_code=500, detail="Invalid authentication response")
        
        if not hasattr(auth_response.session, 'access_token'):
            logger.error(f"Auth response missing access_token: {auth_response.session}")
            raise HTTPException(status_code=500, detail="Authentication response missing access token")
        
        # Create user profile in our database
        user = User(
            supabase_user_id=auth_response.user.id,
            email=auth_request.email,
            email_verified=auth_response.user.email_confirmed_at is not None,
            name=auth_request.name,
            age=auth_request.age,
            weight=auth_request.weight,
            height=auth_request.height,
            fitness_goals=auth_request.fitness_goals,
            fitness_goal_type=auth_request.fitness_goal_type,
            injuries_limitations=auth_request.injuries_limitations
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User created successfully with Supabase Auth: {auth_request.email}")
        
        return AuthResponse(
            access_token=auth_response.session.access_token,
            user=user,
            expires_in=auth_response.session.expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign up failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signup-simple", response_model=AuthResponse)
async def sign_up_simple(
    auth_request: AuthRequest,
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign up a new user with just email and password"""
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == auth_request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Sign up with Supabase Auth (create basic user)
        auth_response = await auth_service.sign_up_with_email(
            email=auth_request.email,
            password=auth_request.password,
            user_data={
                "name": "New User",  # Default name
                "age": 25,  # Default age
                "weight": 70.0,  # Default weight
                "height": 175.0,  # Default height
                "fitness_goals": "Build muscle",  # Default goal
                "fitness_goal_type": "building_muscle",  # Default type
                "injuries_limitations": None
            }
        )
        
        # Check if auth_response is None
        if auth_response is None:
            logger.error("Auth service returned None response")
            raise HTTPException(status_code=500, detail="Authentication service error")
        
        # Validate auth_response structure
        if not hasattr(auth_response, 'user') or not hasattr(auth_response, 'session'):
            logger.error(f"Invalid auth response structure: {auth_response}")
            raise HTTPException(status_code=500, detail="Invalid authentication response")
        
        if not hasattr(auth_response.session, 'access_token'):
            logger.error(f"Auth response missing access_token: {auth_response.session}")
            raise HTTPException(status_code=500, detail="Authentication response missing access token")
        
        # Create basic user profile in our database
        user = User(
            supabase_user_id=auth_response.user.id,
            email=auth_request.email,
            email_verified=auth_response.user.email_confirmed_at is not None,
            name="New User",  # Will be updated during onboarding
            age=25,  # Will be updated during onboarding
            weight=70.0,  # Will be updated during onboarding
            height=175.0,  # Will be updated during onboarding
            fitness_goals="Build muscle",  # Will be updated during onboarding
            fitness_goal_type="building_muscle",  # Will be updated during onboarding
            injuries_limitations=None
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Basic user created successfully: {auth_request.email}")
        
        return AuthResponse(
            access_token=auth_response.session.access_token,
            user=user,
            expires_in=auth_response.session.expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simple sign up failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin", response_model=AuthResponse)
async def sign_in(
    auth_request: AuthRequest,
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign in an existing user"""
    try:
        # First, try to find user in our database
        result = await db.execute(
            select(User).where(User.email == auth_request.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Sign in with Supabase Auth (with fallback handled by service)
        auth_response = await auth_service.sign_in_with_email(
            email=auth_request.email,
            password=auth_request.password
        )
        
        # Update user's last login time
        user.last_login = datetime.utcnow()
        await db.commit()
        
        logger.info(f"User signed in successfully: {auth_request.email}")
        
        return AuthResponse(
            access_token=auth_response.session.access_token,
            user=user,
            expires_in=auth_response.session.expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign in failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/oauth/{provider}", response_model=AuthResponse)
async def oauth_sign_in(
    provider: str,
    oauth_request: OAuthRequest,
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign in with OAuth provider (Google/Apple)"""
    try:
        # Sign in with OAuth
        auth_response = await auth_service.sign_in_with_oauth(
            provider,
            oauth_request.access_token
        )
        
        # Get or create user profile
        result = await db.execute(
            select(User).where(User.supabase_user_id == auth_response.user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user and oauth_request.user_info:
            # Create new user profile from OAuth data
            user = User(
                supabase_user_id=auth_response.user.id,
                email=auth_response.user.email,
                email_verified=auth_response.user.email_confirmed_at is not None,
                name=oauth_request.user_info.get("name", "Unknown"),
                age=oauth_request.user_info.get("age", 25),
                weight=oauth_request.user_info.get("weight", 70.0),
                height=oauth_request.user_info.get("height", 175.0),
                fitness_goals=oauth_request.user_info.get("fitness_goals", "Build muscle"),
                fitness_goal_type=oauth_request.user_info.get("fitness_goal_type", "muscle_hypertrophy"),
                injuries_limitations=oauth_request.user_info.get("injuries_limitations")
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        logger.info(f"OAuth sign in successful for {provider}")
        
        return AuthResponse(
            access_token=auth_response.session.access_token,
            user=user,
            expires_in=auth_response.session.expires_in
        )
        
    except Exception as e:
        logger.error(f"OAuth sign in failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apple", response_model=AuthResponse)
async def sign_in_with_apple(
    request_data: dict,
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign in with Apple"""
    try:
        # Extract data from request
        apple_user_id = request_data.get("apple_user_id")
        email = request_data.get("email")
        name = request_data.get("name")
        identity_token = request_data.get("identity_token")
        nonce = request_data.get("nonce")
        
        if not apple_user_id:
            raise HTTPException(status_code=400, detail="Apple user ID is required")
        
        if not identity_token:
            raise HTTPException(status_code=400, detail="Apple identity token is required")
        
        if not nonce:
            raise HTTPException(status_code=400, detail="Nonce is required")
        
        logger.info(f"Apple sign in attempt for user: {apple_user_id}")
        
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.supabase_user_id == apple_user_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # User exists, sign them in
            logger.info(f"Apple sign in successful for existing user: {existing_user.email}")
            
            # Generate a session token (in a real implementation, you'd verify with Apple)
            # For now, we'll create a simple token
            session_token = f"apple_session_{apple_user_id}"
            
            return AuthResponse(
                access_token=session_token,
                user=existing_user,
                expires_in=3600
            )
        else:
            # New user, create account
            if not email:
                raise HTTPException(status_code=400, detail="Email is required for new users")
            
            # Create user in our database
            user = User(
                supabase_user_id=apple_user_id,
                email=email,
                email_verified=True,  # Apple emails are verified
                name=name or "Apple User",
                age=25,  # Default values
                weight=70.0,
                height=175.0,
                fitness_goals="Build muscle",
                fitness_goal_type="muscle_hypertrophy",
                injuries_limitations=None
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Apple sign up successful for new user: {email}")
            
            # Generate a session token
            session_token = f"apple_session_{apple_user_id}"
            
            return AuthResponse(
                access_token=session_token,
                user=user,
                expires_in=3600
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apple sign in failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/google", response_model=AuthResponse)
async def sign_in_with_google(
    request_data: dict,
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign in with Google"""
    try:
        # Extract data from request
        provider = request_data.get("provider")
        client_id = request_data.get("client_id")
        redirect_uri = request_data.get("redirect_uri")
        
        if provider != "google":
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        # For now, we'll create a mock Google user for testing
        # In a real implementation, you'd exchange the authorization code for user data
        google_user_id = f"google_{hash(client_id) % 1000000}"  # Mock user ID
        email = f"user_{google_user_id}@gmail.com"  # Mock email
        name = "Google User"  # Mock name
        
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.supabase_user_id == google_user_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # User exists, sign them in
            logger.info(f"Google sign in successful for existing user: {existing_user.email}")
            
            # Generate a session token
            session_token = f"google_session_{google_user_id}"
            
            return AuthResponse(
                access_token=session_token,
                user=existing_user,
                expires_in=3600
            )
        else:
            # New user, create account
            user = User(
                supabase_user_id=google_user_id,
                email=email,
                email_verified=True,  # Google emails are verified
                name=name,
                age=25,  # Default values
                weight=70.0,
                height=175.0,
                fitness_goals="Build muscle",
                fitness_goal_type="muscle_hypertrophy",
                injuries_limitations=None
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Google sign up successful for new user: {email}")
            
            # Generate a session token
            session_token = f"google_session_{google_user_id}"
            
            return AuthResponse(
                access_token=session_token,
                user=user,
                expires_in=3600
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google sign in failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify", response_model=TokenVerificationResponse)
async def verify_token(
    token_request: TokenVerificationRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Verify JWT token"""
    try:
        token_data = await auth_service.verify_token(token_request.token)
        
        if token_data:
            return TokenVerificationResponse(
                valid=True,
                user_id=token_data.get("sub"),
                email=token_data.get("email"),
                email_verified=token_data.get("email_verified", False)
            )
        else:
            return TokenVerificationResponse(valid=False)
            
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return TokenVerificationResponse(valid=False)

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    reset_request: PasswordResetRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Send password reset email"""
    try:
        await auth_service.reset_password(reset_request.email)
        
        return PasswordResetResponse(
            success=True,
            message="Password reset email sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signout")
async def sign_out(
    current_user: User = Depends(get_current_user),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign out user"""
    try:
        await auth_service.sign_out("")  # Token will be handled by Supabase client
        
        return APIResponse(
            success=True,
            message="User signed out successfully"
        )
        
    except Exception as e:
        logger.error(f"Sign out failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=APIResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return APIResponse(
        success=True,
        message="User profile retrieved successfully",
        data=current_user
    )

@router.post("/google/callback", response_model=AuthResponse)
async def google_oauth_callback(
    request_data: dict,
    db: AsyncSession = Depends(get_async_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Handle Google OAuth callback from iOS app"""
    try:
        code = request_data.get("code")
        redirect_uri = request_data.get("redirect_uri")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        # Get client secret from environment
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        if not client_secret:
            raise HTTPException(status_code=500, detail="Google Client Secret not configured")
        
        token_data = {
            "client_id": "833450458896-topin53mq4jsb03r6d4od625f6en4ra3.apps.googleusercontent.com",
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_info = token_response.json()
            access_token = token_info.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Get user info from Google
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            user_response = await client.get(user_info_url, headers=headers)
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info from Google")
            
            user_info = user_response.json()
            
            # Create or get user from database
            google_user_id = user_info.get("id")
            email = user_info.get("email")
            name = user_info.get("name", "Google User")
            
            # Check if user exists
            result = await db.execute(
                select(User).where(User.supabase_user_id == f"google_{google_user_id}")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # Create new user
                user = User(
                    supabase_user_id=f"google_{google_user_id}",
                    email=email,
                    email_verified=user_info.get("verified_email", False),
                    name=name,
                    age=25,  # Default values
                    weight=70.0,
                    height=175.0,
                    fitness_goals="Building muscle",
                    fitness_goal_type="building_muscle",
                    injuries_limitations=None
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            
            logger.info(f"Google OAuth sign in successful for user: {user.email}")
            
            return AuthResponse(
                access_token=access_token,
                user=user,
                expires_in=3600
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/test-signup", response_model=AuthResponse)
async def test_sign_up(
    auth_request: AuthSignUpRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Test signup without Supabase Auth - direct database creation"""
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == auth_request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create a local user ID
        import uuid
        local_user_id = f"local_{uuid.uuid4().hex}"
        
        # Create user profile in our database
        user = User(
            supabase_user_id=local_user_id,
            email=auth_request.email,
            email_verified=False,
            name=auth_request.name,
            age=auth_request.age,
            weight=auth_request.weight,
            height=auth_request.height,
            fitness_goals=auth_request.fitness_goals,
            fitness_goal_type=auth_request.fitness_goal_type,
            injuries_limitations=auth_request.injuries_limitations
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Test user created successfully: {auth_request.email}")
        
        return AuthResponse(
            access_token=f"test_token_{local_user_id}",
            user=user,
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test signup failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/direct-signup", response_model=AuthResponse)
async def direct_sign_up(
    auth_request: AuthSignUpRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Direct signup bypassing Supabase Auth entirely"""
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == auth_request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create a local user ID
        import uuid
        local_user_id = f"direct_{uuid.uuid4().hex}"
        
        # Create user profile directly in our database
        user = User(
            supabase_user_id=local_user_id,
            email=auth_request.email,
            email_verified=False,
            name=auth_request.name,
            age=auth_request.age,
            weight=auth_request.weight,
            height=auth_request.height,
            fitness_goals=auth_request.fitness_goals,
            fitness_goal_type=auth_request.fitness_goal_type,
            injuries_limitations=auth_request.injuries_limitations
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Direct user created successfully: {auth_request.email}")
        
        return AuthResponse(
            access_token=f"direct_token_{local_user_id}",
            user=user,
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Direct signup failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/.well-known/apple-app-site-association")
async def apple_app_site_association():
    """Serve Apple App Site Association file for domain verification"""
    return {
        "applinks": {
            "apps": [],
            "details": [
                {
                    "appID": "TEAM_ID.com.yourcompany.slate",
                    "paths": ["*"]
                }
            ]
        },
        "webcredentials": {
            "apps": ["TEAM_ID.com.yourcompany.slate"]
        }
    }
