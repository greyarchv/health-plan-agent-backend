from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_sync_db, get_async_db
from ..models import User
from ..schemas import UserCreate, UserUpdate, User as UserSchema, APIResponse
from sqlalchemy import select
import json

router = APIRouter(tags=["users"])

@router.get("/", response_model=APIResponse)
async def get_all_users(db: AsyncSession = Depends(get_async_db)):
    """Get all user profiles"""
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(users)} users successfully",
            data=[UserSchema.from_orm(user) for user in users]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=APIResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new user profile"""
    try:
        # Create new user with authentication fields
        db_user = User(
            # Authentication fields (set to None for regular user creation)
            supabase_user_id=None,
            email=None,
            email_verified=False,
            # Profile fields
            name=user_data.name,
            age=user_data.age,
            weight=user_data.weight,
            height=user_data.height,
            fitness_goals=user_data.fitness_goals,
            fitness_goal_type=user_data.fitness_goal_type,
            injuries_limitations=user_data.injuries_limitations
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return APIResponse(
            success=True,
            message="User created successfully",
            data=UserSchema.from_orm(db_user)
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apple", response_model=dict)
async def create_apple_user(user_data: dict, db: AsyncSession = Depends(get_async_db)):
    """Create a new user from Apple Sign-In or return existing user"""
    try:
        print(f"🍎 Apple Sign-In request received: {user_data}")
        
        # Extract data from Apple Sign-In
        supabase_user_id = user_data.get("supabase_user_id")
        email = user_data.get("email")
        name = user_data.get("name")
        provider = user_data.get("provider", "apple")
        
        print(f"🍎 Extracted data - ID: {supabase_user_id}, Email: {email}, Name: {name}")
        
        # Check if user already exists
        existing_user = await db.execute(
            select(User).where(User.supabase_user_id == supabase_user_id)
        )
        existing_user = existing_user.scalar_one_or_none()
        
        if existing_user:
            print(f"🍎 Found existing user with ID: {existing_user.id}")
            # Return existing user
            user_dict = UserSchema.from_orm(existing_user).dict()
            response = {
                "user": user_dict,
                "access_token": "apple_auth_token"  # Placeholder token
            }
            print(f"🍎 Returning existing user: {response}")
            return response
        
        print(f"🍎 Creating new user...")
        
        # Create new user with Apple authentication data
        db_user = User(
            supabase_user_id=supabase_user_id,
            email=email if email else None,
            email_verified=user_data.get("email_verified", True),
            name=name,
            age=25,  # Default age for Apple Sign-In users
            weight=70.0,  # Default weight in kg
            height=170.0,  # Default height in cm
            fitness_goals="Building Muscle",  # Default goal
            fitness_goal_type="building_muscle",  # Default goal type
            injuries_limitations="None"  # Default to no injuries
        )
        
        print(f"🍎 Created User object: {db_user}")
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        print(f"🍎 User saved to database with ID: {db_user.id}")
        
        # Convert to dict for response
        user_dict = UserSchema.from_orm(db_user).dict()
        print(f"🍎 User dict: {user_dict}")
        
        # Return format expected by iOS app
        response = {
            "user": user_dict,
            "access_token": "apple_auth_token"  # Placeholder token
        }
        
        print(f"🍎 Returning response: {response}")
        return response
    
    except Exception as e:
        print(f"❌ Error in create_apple_user: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=APIResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get user profile by ID"""
    try:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return APIResponse(
            success=True,
            message="User retrieved successfully",
            data=UserSchema.from_orm(user)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=APIResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_async_db)):
    """Update user profile"""
    try:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update only provided fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return APIResponse(
            success=True,
            message="User updated successfully",
            data=UserSchema.from_orm(user)
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 