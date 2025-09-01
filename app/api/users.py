from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_sync_db, get_async_db
from ..models import User
from ..schemas import UserCreate, UserUpdate, User as UserSchema, APIResponse
from sqlalchemy import select
import json

router = APIRouter(prefix="/user", tags=["users"])

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
        # Create new user
        db_user = User(
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