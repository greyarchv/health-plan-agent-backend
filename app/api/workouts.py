from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta
from ..database import get_sync_db, get_async_db
from ..models import User, WorkoutLog
from ..schemas import WorkoutLogCreate, WorkoutLog as WorkoutLogSchema, WorkoutPlan, APIResponse
# Removed AI orchestrator dependency - using JSON-based workout plans
import json
from ..services.workout_plan_service import WorkoutPlanService

router = APIRouter(prefix="/workout", tags=["workouts"])

@router.get("/{user_id}", response_model=APIResponse)
async def get_workout_plan(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get personalized workout plan for user"""
    try:
        # Get user data
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare user data for workout generation
        user_data = {
            "age": user.age,
            "weight": user.weight,
            "height": user.height,
            "fitness_goals": user.fitness_goals,
            "fitness_goal_type": user.fitness_goal_type,
            "injuries_limitations": user.injuries_limitations
        }
        
        # Load workout plan from database or fallback to JSON file
        goal_type = user.fitness_goal_type or "building_muscle"
        
        # Initialize workout plan service
        workout_service = WorkoutPlanService()
        
        try:
            # First, try to get plan from database
            plan_data = await workout_service.get_plan(goal_type)
            
            if plan_data:
                # Plan found in database
                print(f"✅ Plan '{goal_type}' loaded from database")
            else:
                # Fallback to JSON file
                print(f"📁 Plan '{goal_type}' not found in database, loading from JSON file")
                with open("app/data/workout_plans.json", "r") as f:
                    workout_plans = json.load(f)
                
                if goal_type in workout_plans:
                    plan_data = workout_plans[goal_type]
                else:
                    # Use default plan if goal type not found
                    plan_data = workout_plans.get("building_muscle", {})
            
            # Convert plan data to WorkoutPlan format
            if plan_data and "days" in plan_data:
                workout_plan = WorkoutPlan(
                    week_plan=[
                        {"day": day, "focus": "Workout", "exercises": exercises}
                        for day, exercises in plan_data.get("days", {}).items()
                    ],
                    exercises=[
                        {"name": exercise.split(" — ")[0], "sets": 3, "reps": "8-12", "weight": "Progressive"}
                        for exercises in plan_data.get("days", {}).values()
                        for exercise in exercises
                    ]
                )
            else:
                # Fallback to default plan structure
                workout_plan = WorkoutPlan(
                    week_plan=[
                        {"day": "Monday", "focus": "Upper Body", "exercises": ["Bench Press", "Rows", "Shoulder Press"]},
                        {"day": "Tuesday", "focus": "Lower Body", "exercises": ["Squats", "Deadlifts", "Lunges"]},
                        {"day": "Wednesday", "focus": "Rest", "exercises": ["Light Cardio", "Stretching"]},
                        {"day": "Thursday", "focus": "Upper Body", "exercises": ["Pull-ups", "Dips", "Bicep Curls"]},
                        {"day": "Friday", "focus": "Lower Body", "exercises": ["Leg Press", "Romanian Deadlifts"]},
                        {"day": "Saturday", "focus": "Full Body", "exercises": ["Burpees", "Mountain Climbers"]},
                        {"day": "Sunday", "focus": "Rest", "exercises": ["Active Recovery", "Stretching"]}
                    ],
                    exercises=[
                        {"name": "Bench Press", "sets": 3, "reps": "8-12", "weight": "Progressive"},
                        {"name": "Squats", "sets": 4, "reps": "8-12", "weight": "Progressive"},
                        {"name": "Deadlifts", "sets": 3, "reps": "6-8", "weight": "Progressive"}
                    ]
                )
        except Exception as e:
            print(f"⚠️ Error loading plan from database/JSON: {e}")
            # Fallback to default plan
            workout_plan = WorkoutPlan(
                week_plan=[
                    {"day": "Monday", "focus": "Upper Body", "exercises": ["Bench Press", "Rows", "Shoulder Press"]},
                    {"day": "Tuesday", "focus": "Lower Body", "exercises": ["Squats", "Deadlifts", "Lunges"]},
                    {"day": "Wednesday", "focus": "Rest", "exercises": ["Light Cardio", "Stretching"]},
                    {"day": "Thursday", "focus": "Upper Body", "exercises": ["Pull-ups", "Dips", "Bicep Curls"]},
                    {"day": "Friday", "focus": "Lower Body", "exercises": ["Leg Press", "Romanian Deadlifts"]},
                    {"day": "Saturday", "focus": "Full Body", "exercises": ["Burpees", "Mountain Climbers"]},
                    {"day": "Sunday", "focus": "Rest", "exercises": ["Active Recovery", "Stretching"]}
                ],
                exercises=[
                    {"name": "Bench Press", "sets": 3, "reps": "8-12", "weight": "Progressive"},
                    {"name": "Squats", "sets": 4, "reps": "8-12", "weight": "Progressive"},
                    {"name": "Deadlifts", "sets": 3, "reps": "6-8", "weight": "Progressive"}
                ]
            )
        
        return APIResponse(
            success=True,
            message="Workout plan loaded successfully",
            data={
                "plan": workout_plan.dict()
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log", response_model=APIResponse)
async def log_workout(workout_data: WorkoutLogCreate, user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Log a workout session"""
    try:
        # Verify user exists
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create workout log entry
        workout_log = WorkoutLog(
            user_id=user_id,
            exercise_name=workout_data.exercise_name,
            sets=workout_data.sets,
            reps=workout_data.reps,
            weight=workout_data.weight,
            notes=workout_data.notes
        )
        
        db.add(workout_log)
        await db.commit()
        await db.refresh(workout_log)
        
        return APIResponse(
            success=True,
            message="Workout logged successfully",
            data=WorkoutLogSchema.from_orm(workout_log)
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}", response_model=APIResponse)
async def get_workout_history(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get user's workout history"""
    try:
        # Verify user exists
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get workout logs for user
        stmt = select(WorkoutLog).where(WorkoutLog.user_id == user_id).order_by(WorkoutLog.workout_date.desc())
        result = await db.execute(stmt)
        workout_logs = result.scalars().all()
        
        return APIResponse(
            success=True,
            message="Workout history retrieved successfully",
            data=[WorkoutLogSchema.from_orm(log) for log in workout_logs]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/plans/discover", response_model=APIResponse)
async def discover_workout_plans(
    category: str = None,
    difficulty: str = None,
    plan_type: str = None,
    limit: int = 20
):
    """Discover available workout plans with rich metadata for frontend display"""
    try:
        workout_service = WorkoutPlanService()
        
        # Get all plans from database
        db_plans = await workout_service.get_all_plans()
        
        # Get plans from JSON file as fallback
        json_plans = {}
        try:
            with open("app/data/workout_plans.json", "r") as f:
                json_plans = json.load(f)
        except FileNotFoundError:
            pass
        
        # Combine and format plans for frontend
        all_plans = {}
        
        # Add database plans (generated plans)
        for plan_id, plan_data in db_plans.items():
            # Get metadata for this plan
            metadata = await workout_service.get_plan_metadata(plan_id)
            if metadata:
                all_plans[plan_id] = {
                    "plan_data": plan_data,
                    "metadata": metadata["metadata"],
                    "created_at": metadata["created_at"],
                    "updated_at": metadata["updated_at"],
                    "source": "database"
                }
        
        # Add JSON plans (default plans)
        for plan_id, plan_data in json_plans.items():
            if plan_id not in all_plans:  # Don't override database plans
                all_plans[plan_id] = {
                    "plan_data": plan_data,
                    "metadata": {
                        "type": "default",
                        "category": "general",
                        "difficulty": "intermediate",
                        "duration": "12_weeks"
                    },
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "source": "json"
                }
        
        # Filter plans based on query parameters
        filtered_plans = {}
        for plan_id, plan_info in all_plans.items():
            # Apply category filter
            if category and plan_info["metadata"].get("category") != category:
                continue
                
            # Apply difficulty filter
            if difficulty and plan_info["metadata"].get("difficulty") != difficulty:
                continue
                
            # Apply plan type filter
            if plan_type and plan_info["metadata"].get("type") != plan_type:
                continue
                
            filtered_plans[plan_id] = plan_info
        
        # Limit results
        limited_plans = dict(list(filtered_plans.items())[:limit])
        
        # Format response for frontend
        plans_for_frontend = {}
        for plan_id, plan_info in limited_plans.items():
            plans_for_frontend[plan_id] = {
                "overview": plan_info["plan_data"].get("overview", ""),
                "weekly_split": plan_info["plan_data"].get("weekly_split", []),
                "global_rules": plan_info["plan_data"].get("global_rules", []),
                "days": plan_info["plan_data"].get("days", {}),
                "conditioning_and_recovery": plan_info["plan_data"].get("conditioning_and_recovery", []),
                "nutrition": plan_info["plan_data"].get("nutrition", {}),
                "metadata": plan_info["metadata"],
                "source": plan_info["source"]
            }
        
        return APIResponse(
            success=True,
            message="Workout plans discovered successfully",
            data={
                "plans": plans_for_frontend,
                "total_count": len(filtered_plans),
                "returned_count": len(limited_plans),
                "filters_applied": {
                    "category": category,
                    "difficulty": difficulty,
                    "plan_type": plan_type
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discovering plans: {str(e)}")

@router.get("/plans/categories", response_model=APIResponse)
async def get_plan_categories():
    """Get all available plan categories for frontend filtering"""
    try:
        workout_service = WorkoutPlanService()
        
        # Get all plans to extract categories
        db_plans = await workout_service.get_all_plans()
        
        # Get plans from JSON file
        json_plans = {}
        try:
            with open("app/data/workout_plans.json", "r") as f:
                json_plans = json.load(f)
        except FileNotFoundError:
            pass
        
        # Collect all categories
        categories = set()
        
        # Add database plan categories
        for plan_id, plan_data in db_plans.items():
            metadata = await workout_service.get_plan_metadata(plan_id)
            if metadata and metadata["metadata"].get("category"):
                categories.add(metadata["metadata"]["category"])
        
        # Add JSON plan categories
        for plan_id, plan_data in json_plans.items():
            # Default categories for JSON plans
            if "muscle" in plan_id.lower():
                categories.add("strength")
            elif "weight" in plan_id.lower():
                categories.add("weight_loss")
            elif "endurance" in plan_id.lower():
                categories.add("endurance")
            else:
                categories.add("general")
        
        return APIResponse(
            success=True,
            message="Plan categories retrieved successfully",
            data={
                "categories": list(categories),
                "total_categories": len(categories)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")

@router.get("/plans/difficulties", response_model=APIResponse)
async def get_plan_difficulties():
    """Get all available plan difficulties for frontend filtering"""
    try:
        workout_service = WorkoutPlanService()
        
        # Get all plans to extract difficulties
        db_plans = await workout_service.get_all_plans()
        
        # Get plans from JSON file
        json_plans = {}
        try:
            with open("app/data/workout_plans.json", "r") as f:
                json_plans = json.load(f)
        except FileNotFoundError:
            pass
        
        # Collect all difficulties
        difficulties = set()
        
        # Add database plan difficulties
        for plan_id, plan_data in db_plans.items():
            metadata = await workout_service.get_plan_metadata(plan_id)
            if metadata and metadata["metadata"].get("difficulty"):
                difficulties.add(metadata["metadata"]["difficulty"])
        
        # Add JSON plan difficulties
        for plan_id, plan_data in json_plans.items():
            # Default difficulties for JSON plans
            if "beginner" in plan_id.lower():
                difficulties.add("beginner")
            elif "advanced" in plan_id.lower():
                difficulties.add("advanced")
            else:
                difficulties.add("intermediate")
        
        return APIResponse(
            success=True,
            message="Plan difficulties retrieved successfully",
            data={
                "difficulties": list(difficulties),
                "total_difficulties": len(difficulties)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting difficulties: {str(e)}") 