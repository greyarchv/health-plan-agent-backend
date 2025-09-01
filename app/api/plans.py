from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import json
import os
from ..database import get_async_db
from ..models import User
from ..schemas import APIResponse

router = APIRouter(prefix="/plans", tags=["workout_plans"])

@router.get("/available")
async def get_available_plans():
    """Get all available workout plans with metadata."""
    try:
        index_path = "app/data/workout_plans/index.json"
        with open(index_path, "r") as f:
            plan_index = json.load(f)
        
        return APIResponse(
            success=True,
            message="Available plans retrieved successfully",
            data=plan_index
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan index not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plans: {str(e)}")

@router.get("/{plan_id}")
async def get_workout_plan(plan_id: str):
    """Get specific workout plan by ID."""
    try:
        # Load plan index
        index_path = "app/data/workout_plans/index.json"
        with open(index_path, "r") as f:
            plan_index = json.load(f)
        
        if plan_id not in plan_index["plans"]:
            raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found")
        
        plan_meta = plan_index["plans"][plan_id]
        file_path = f"app/data/workout_plans/{plan_meta['file_path']}"
        
        # Load plan content
        with open(file_path, "r") as f:
            plan_data = json.load(f)
        
        return APIResponse(
            success=True,
            message=f"Plan '{plan_id}' loaded successfully",
            data={
                "metadata": plan_meta,
                "plan": plan_data
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plan: {str(e)}")

@router.get("/categories/{category}")
async def get_plans_by_category(category: str):
    """Get all plans in a specific category."""
    try:
        index_path = "app/data/workout_plans/index.json"
        with open(index_path, "r") as f:
            plan_index = json.load(f)
        
        # Filter plans by category
        category_plans = {
            plan_id: plan_data 
            for plan_id, plan_data in plan_index["plans"].items()
            if plan_data.get("category") == category and plan_data.get("is_active", True)
        }
        
        return APIResponse(
            success=True,
            message=f"Plans in category '{category}' retrieved successfully",
            data={
                "category": category,
                "plans": category_plans,
                "count": len(category_plans)
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan index not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plans: {str(e)}")

@router.get("/types/{plan_type}")
async def get_plans_by_type(plan_type: str):
    """Get all plans of a specific type (default, generated, custom)."""
    try:
        index_path = "app/data/workout_plans/index.json"
        with open(index_path, "r") as f:
            plan_index = json.load(f)
        
        # Filter plans by type
        type_plans = {
            plan_id: plan_data 
            for plan_id, plan_data in plan_index["plans"].items()
            if plan_data.get("type") == plan_type and plan_data.get("is_active", True)
        }
        
        return APIResponse(
            success=True,
            message=f"Plans of type '{plan_type}' retrieved successfully",
            data={
                "type": plan_type,
                "plans": type_plans,
                "count": len(type_plans)
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan index not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plans: {str(e)}")
