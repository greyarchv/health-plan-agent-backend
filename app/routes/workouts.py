"""
Workout Routes

Handles workout plan generation, exercise tracking, and progress monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
from ..database import get_async_db
from ..models import User, WorkoutPlan, ExerciseRecord, WorkoutLog
from ..schemas import APIResponse, WorkoutLogCreate
import json # Added for workout plan discovery endpoints

# Import the workout plan manager
try:
    from ..utils.workout_plan_manager import workout_plan_manager
    WORKOUT_PLAN_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ workout_plan_manager not available")
    WORKOUT_PLAN_MANAGER_AVAILABLE = False

router = APIRouter()

@router.get("/test", response_model=APIResponse)
async def test_workout_router():
    """Test endpoint to verify workout router is working"""
    return APIResponse(
        success=True,
        message="Workout router is working",
        data={"status": "ok"}
    )

@router.get("/history/{user_id}", response_model=APIResponse)
async def get_workout_history(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get workout history for a user"""
    try:
        # Use raw SQL to avoid any potential issues
        from sqlalchemy import text
        
        # Verify user exists using raw SQL
        user_check_query = text("SELECT id FROM users WHERE id = :user_id")
        result = await db.execute(user_check_query, {"user_id": user_id})
        user_exists = result.fetchone()
        
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get workout history
        query = text("""
            SELECT 
                exercise_name,
                sets,
                reps,
                weight,
                workout_date,
                notes
            FROM workout_logs 
            WHERE user_id = :user_id
            ORDER BY workout_date DESC
            LIMIT 50
        """)
        
        result = await db.execute(query, {"user_id": user_id})
        workout_logs = result.fetchall()
        
        # Convert to list of dictionaries
        history_data = []
        for log in workout_logs:
            history_data.append({
                "exercise_name": log.exercise_name,
                "sets": int(log.sets) if log.sets else 0,
                "reps": int(log.reps) if log.reps else 0,
                "weight": float(log.weight) if log.weight else 0.0,
                "workout_date": log.workout_date.isoformat() if log.workout_date else None,
                "notes": log.notes
            })
        
        return APIResponse(
            success=True,
            message="Workout history retrieved successfully",
            data={
                "workout_history": history_data,
                "total_workouts": len(history_data)
            }
        )
        
    except Exception as e:
        print(f"Error in workout history endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/exercise-history/{user_id}/{exercise_name}", response_model=APIResponse)
async def get_exercise_history(
    user_id: int,
    exercise_name: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get exercise history for a specific exercise"""
    try:
        # Use raw SQL to avoid any potential issues
        from sqlalchemy import text
        
        # Verify user exists using raw SQL
        user_check_query = text("SELECT id FROM users WHERE id = :user_id")
        result = await db.execute(user_check_query, {"user_id": user_id})
        user_exists = result.fetchone()
        
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get the last workout for this exercise
        query = text("""
            SELECT 
                exercise_name,
                sets,
                reps,
                weight,
                workout_date
            FROM workout_logs 
            WHERE user_id = :user_id AND exercise_name = :exercise_name
            ORDER BY workout_date DESC
            LIMIT 1
        """)
        
        result = await db.execute(query, {"user_id": user_id, "exercise_name": exercise_name})
        last_workout = result.fetchone()
        
        if last_workout:
            # User has done this exercise before
            print(f"📊 Found last workout: {last_workout}")
            
            # Handle potential type issues
            weight = float(last_workout.weight) if last_workout.weight else 0.0
            sets = int(last_workout.sets) if last_workout.sets else 3
            reps = int(last_workout.reps) if last_workout.reps else 10
            
            # Handle workout_date (could be string or datetime)
            workout_date = last_workout.workout_date
            if hasattr(workout_date, 'isoformat'):
                date_str = workout_date.isoformat()
            else:
                date_str = str(workout_date) if workout_date else None
            
            suggested_weight = weight + 2.5  # Progressive overload
            
            return APIResponse(
                success=True,
                message="Exercise history retrieved successfully",
                data={
                    "is_new_exercise": False,
                    "last_workout": {
                        "weight": weight,
                        "sets": sets,
                        "reps": reps,
                        "date": date_str
                    },
                    "suggested_weight": suggested_weight,
                    "suggested_sets": sets,
                    "suggested_reps": reps
                }
            )
        else:
            # New exercise for this user
            return APIResponse(
                success=True,
                message="Exercise history retrieved successfully",
                data={
                    "is_new_exercise": True,
                    "last_workout": None,
                    "suggested_weight": None,
                    "suggested_sets": 3,
                    "suggested_reps": 10
                }
            )
        
    except Exception as e:
        print(f"Error in exercise history endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/log", response_model=APIResponse)
async def log_workout(workout_data: WorkoutLogCreate, user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Log a workout session"""
    try:
        # Use raw SQL to avoid any potential issues
        from sqlalchemy import text
        
        # Verify user exists using raw SQL
        user_check_query = text("SELECT id FROM users WHERE id = :user_id")
        result = await db.execute(user_check_query, {"user_id": user_id})
        user_exists = result.fetchone()
        
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Insert workout log using raw SQL
        insert_query = text("""
            INSERT INTO workout_logs (user_id, exercise_name, sets, reps, weight, notes, workout_date)
            VALUES (:user_id, :exercise_name, :sets, :reps, :weight, :notes, :workout_date)
            RETURNING id
        """)
        
        result = await db.execute(insert_query, {
            "user_id": user_id,
            "exercise_name": workout_data.exercise_name,
            "sets": workout_data.sets,
            "reps": workout_data.reps,
            "weight": workout_data.weight,
            "notes": workout_data.notes or "",
            "workout_date": datetime.utcnow()
        })
        
        # Get the inserted record ID
        workout_id = result.scalar()
        
        await db.commit()
        
        print(f"📊 Database: Stored workout log - User: {user_id}, Exercise: {workout_data.exercise_name}, ID: {workout_id}")
        
        return APIResponse(
            success=True,
            message="Workout logged successfully",
            data={
                "id": workout_id,
                "user_id": user_id,
                "exercise_name": workout_data.exercise_name,
                "sets": workout_data.sets,
                "reps": workout_data.reps,
                "weight": workout_data.weight,
                "notes": workout_data.notes or "",
                "workout_date": datetime.utcnow().isoformat()
            }
        )
    
    except Exception as e:
        print(f"Error in log_workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exercise-catalog", response_model=APIResponse)
async def get_exercise_catalog():
    """Get the comprehensive exercise catalog organized by muscle groups"""
    try:
        # Comprehensive exercise catalog with distinct names
        exercise_catalog = {
            "Chest": [
                "Bench Press", "Incline Bench Press", "Decline Bench Press", "Push-Up", 
                "Dumbbell Chest Press", "Incline Dumbbell Press", "Decline Dumbbell Press",
                "Cable Chest Press", "Machine Chest Press", "Dumbbell Chest Fly",
                "Cable Chest Fly", "Pec Deck", "Smith Machine Bench Press"
            ],
            "Back": [
                "Pull-Up", "Chin-Up", "Bent-Over Row", "Barbell Row", "Lat Pulldown",
                "T-Bar Row", "Back Face Pull", "Cable Row", "Machine Row",
                "Dumbbell Row", "Inverted Row", "Seated Cable Row"
            ],
            "Shoulders": [
                "Overhead Press", "Military Press", "Lateral Raise", "Front Raise", 
                "Rear Delt Fly", "Shrug", "Arnold Press", "Dumbbell Shoulder Press",
                "Cable Lateral Raise", "Machine Shoulder Press", "Shoulder Face Pull",
                "Upright Row", "Reverse Fly"
            ],
            "Biceps": [
                "Bicep Curl", "Hammer Curl", "Preacher Curl", "Concentration Curl", 
                "Barbell Curl", "Dumbbell Curl", "Cable Curl", "Machine Curl",
                "Incline Dumbbell Curl", "Spider Curl", "Zottman Curl"
            ],
            "Triceps": [
                "Tricep Dip", "Tricep Extension", "Skull Crusher", "Close-Grip Bench Press", 
                "Tricep Pushdown", "Overhead Tricep Extension", "Cable Tricep Extension",
                "Machine Tricep Extension", "Diamond Push-Up", "Tate Press"
            ],
            "Legs": [
                "Squat", "Leg Deadlift", "Leg Press", "Lunge", "Calf Raise", 
                "Romanian Deadlift", "Leg Extension", "Leg Curl", "Hack Squat",
                "Bulgarian Split Squat", "Goblet Squat", "Box Squat", "Sumo Deadlift",
                "Walking Lunge", "Seated Calf Raise", "Standing Calf Raise", "Hip Thrust",
                "Front Squat", "Back Squat", "Ab Wheel", "Machine Dip", "Weighted Dip"
            ],
            "Abs": [
                "Crunch", "Sit-Up", "Plank", "Leg Raise", "Russian Twist",
                "Hanging Leg Raise", "Reverse Crunch", "Bicycle Crunch",
                "Cable Woodchop", "Ab Wheel Rollout", "Mountain Climber"
            ]
        }
        
        return APIResponse(
            success=True,
            message="Exercise catalog retrieved successfully",
            data=exercise_catalog
        )
        
    except Exception as e:
        print(f"Error in exercise catalog endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user-exercise-progress/{user_id}", response_model=APIResponse)
async def get_user_exercise_progress(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get comprehensive exercise progress for a user organized by muscle groups"""
    try:
        # Use raw SQL to get the last workout for each exercise
        from sqlalchemy import text
        
        # Verify user exists
        user_check_query = text("SELECT id FROM users WHERE id = :user_id")
        result = await db.execute(user_check_query, {"user_id": user_id})
        user_exists = result.fetchone()
        
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get the last workout for each exercise using window functions
        query = text("""
            WITH ranked_workouts AS (
                SELECT 
                    exercise_name,
                    sets,
                    reps,
                    weight,
                    workout_date,
                    ROW_NUMBER() OVER (PARTITION BY exercise_name ORDER BY workout_date DESC) as rn
                FROM workout_logs 
                WHERE user_id = :user_id
            )
            SELECT 
                exercise_name,
                sets,
                reps,
                weight,
                workout_date
            FROM ranked_workouts 
            WHERE rn = 1
            ORDER BY exercise_name
        """)
        
        result = await db.execute(query, {"user_id": user_id})
        user_workouts = result.fetchall()
        
        # Organize by muscle groups
        progress_by_muscle_group = {
            "Chest": [],
            "Back": [],
            "Shoulders": [],
            "Biceps": [],
            "Triceps": [],
            "Legs": [],
            "Abs": []
        }
        
        # Define muscle group mappings
        muscle_group_mapping = {
            "Chest": ["bench", "press", "fly", "push-up", "dip", "chest"],
            "Back": ["row", "pull-up", "chin-up", "deadlift", "lat", "back"],
            "Shoulders": ["shoulder", "press", "raise", "delt", "arnold"],
            "Biceps": ["curl", "bicep", "preacher"],
            "Triceps": ["tricep", "extension", "pushdown", "skull"],
            "Legs": ["squat", "lunge", "leg", "deadlift", "calf", "hamstring"],
            "Abs": ["crunch", "sit-up", "plank", "ab", "core"]
        }
        
        # Process each workout and categorize by muscle group
        for workout in user_workouts:
            exercise_name = workout.exercise_name.lower()
            assigned_group = None
            
            # Find the appropriate muscle group
            for group, keywords in muscle_group_mapping.items():
                if any(keyword in exercise_name for keyword in keywords):
                    assigned_group = group
                    break
            
            # If no specific match, try to categorize based on exercise name patterns
            if not assigned_group:
                if any(word in exercise_name for word in ["bench", "press", "fly"]):
                    assigned_group = "Chest"
                elif any(word in exercise_name for word in ["row", "pull", "deadlift"]):
                    assigned_group = "Back"
                elif any(word in exercise_name for word in ["curl", "bicep"]):
                    assigned_group = "Biceps"
                elif any(word in exercise_name for word in ["tricep", "extension"]):
                    assigned_group = "Triceps"
                elif any(word in exercise_name for word in ["squat", "lunge", "leg"]):
                    assigned_group = "Legs"
                else:
                    assigned_group = "Other"  # Fallback category
            
            if assigned_group in progress_by_muscle_group:
                progress_by_muscle_group[assigned_group].append({
                    "exercise_name": workout.exercise_name,
                    "last_weight": float(workout.weight) if workout.weight else None,
                    "last_sets": int(workout.sets) if workout.sets else None,
                    "last_reps": int(workout.reps) if workout.reps else None,
                    "last_workout_date": workout.workout_date.isoformat() if workout.workout_date else None
                })
        
        # Sort exercises within each muscle group by last workout date (most recent first)
        for group in progress_by_muscle_group:
            progress_by_muscle_group[group].sort(
                key=lambda x: x["last_workout_date"] if x["last_workout_date"] else "1900-01-01",
                reverse=True
            )
        
        return APIResponse(
            success=True,
            message="User exercise progress retrieved successfully",
            data=progress_by_muscle_group
        )
        
    except Exception as e:
        print(f"Error in user exercise progress endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/today/{user_id}", response_model=APIResponse)
async def get_todays_workout(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get today's workout plan for a user"""
    try:
        # Get user's workout plan
        workout_plan = await db.execute(
            select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)
        )
        workout_plan = workout_plan.scalar_one_or_none()
        
        if not workout_plan:
            raise HTTPException(status_code=404, detail="No workout plan found for user")
        
        # Determine which day of the week it is (0 = Monday, 6 = Sunday)
        from datetime import datetime
        today = datetime.now()
        day_of_week = today.weekday()  # 0 = Monday, 6 = Sunday
        
        # Map day of week to workout plan day
        day_mapping = {
            0: 0,  # Monday -> Day 1
            1: 1,  # Tuesday -> Day 2
            2: 2,  # Wednesday -> Day 3
            3: 3,  # Thursday -> Day 4
            4: 4,  # Friday -> Day 5
            5: 5,  # Saturday -> Day 6
            6: 6   # Sunday -> Day 7 (Rest)
        }
        
        plan_day_index = day_mapping[day_of_week]
        todays_plan = workout_plan.week_plan[plan_day_index]
        
        return APIResponse(
            success=True,
            message="Today's workout plan retrieved successfully",
            data={
                "today_workout": todays_plan,
                "day_of_week": day_of_week,
                "plan_day": plan_day_index + 1,
                "sets_per_exercise": 3  # Default sets per exercise
            }
        )
        
    except Exception as e:
        print(f"Error in today's workout endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/plan/{user_id}/regenerate", response_model=APIResponse)
async def regenerate_workout_plan(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Force regeneration of workout plan for user using current exercise catalog"""
    try:
        # Get user data
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete existing workout plan
        existing_plan = await db.execute(
            select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)
        )
        existing_plan = existing_plan.scalar_one_or_none()
        
        if existing_plan:
            await db.delete(existing_plan)
            await db.commit()
            print(f"🗑️ Deleted existing workout plan for user {user_id}")
        
        # Generate new workout plan using AI
        if WORKOUT_PLAN_MANAGER_AVAILABLE:
            try:
                # Prepare user data for AI
                user_data = {
                    "name": user.name,
                    "age": user.age,
                    "weight": user.weight,
                    "height": user.height,
                    "fitness_goals": user.fitness_goals,
                    "fitness_goal_type": user.fitness_goal_type,
                    "injuries_limitations": user.injuries_limitations
                }
                
                # Generate workout plan using AI
                ai_plan = workout_plan_manager.generate_workout_plan(user_data, "Create a 7-day workout plan for me")
                
                print(f"🤖 AI Generated Plan: {ai_plan[:200]}...")
                
                # Use the translator to convert AI response to structured format
                workout_plan_data = workout_plan_manager.translate_ai_response(ai_plan, user.fitness_goal_type)
                
            except Exception as e:
                print(f"Error generating AI workout plan: {e}")
                # Use fallback plan if AI generation fails
                workout_plan_data = workout_plan_manager.create_fallback_plan(user.fitness_goal_type)
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to generate workout plan. Please try again later."
                )
        else:
            # AI workout generation not available, use fallback plan
            workout_plan_data = workout_plan_manager.create_fallback_plan(user.fitness_goal_type)
            raise HTTPException(
                status_code=503, 
                detail="Workout plan generation service is currently unavailable. Please try again later."
            )
        
        # Store the new workout plan
        db_workout_plan = WorkoutPlan(
            user_id=user_id,
            week_plan=workout_plan_data["week_plan"],
            goal_type=workout_plan_data["goal_type"]
        )
        db.add(db_workout_plan)
        await db.commit()
        await db.refresh(db_workout_plan)
        
        # Create exercise records for all exercises in the plan
        all_exercises = set()
        for day in workout_plan_data["week_plan"]:
            for exercise in day["exercises"]:
                all_exercises.add(exercise)
        
        # Check existing exercise records
        existing_records = await db.execute(
            select(ExerciseRecord).where(ExerciseRecord.user_id == user_id)
        )
        existing_exercises = {record.exercise_name for record in existing_records.scalars().all()}
        
        # Create new exercise records for exercises not already tracked
        for exercise_name in all_exercises:
            if exercise_name not in existing_exercises:
                exercise_record = ExerciseRecord(
                    user_id=user_id,
                    exercise_name=exercise_name,
                    max_weight=0.0,
                    max_sets=3,
                    max_reps=10
                )
                db.add(exercise_record)
        
        await db.commit()
        
        return APIResponse(
            success=True,
            message="Workout plan regenerated successfully",
            data={
                "plan": {
                    "week_plan": workout_plan_data["week_plan"],
                    "goal_type": workout_plan_data["goal_type"],
                    "created_at": db_workout_plan.created_at.isoformat() if db_workout_plan.created_at else None,
                    "updated_at": db_workout_plan.updated_at.isoformat() if db_workout_plan.updated_at else None
                },
                "ai_recommendation": "I've regenerated your workout plan using the latest exercise catalog. This plan is designed to help you achieve your fitness goals with a balanced approach to muscle development and recovery."
            }
        )
        
    except Exception as e:
        print(f"Error in workout plan regeneration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/plan/{user_id}", response_model=APIResponse)
async def get_workout_plan(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get personalized workout plan for user"""
    try:
        # Get user data
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user has a stored workout plan
        workout_plan = await db.execute(
            select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)
        )
        workout_plan = workout_plan.scalar_one_or_none()
        
        if workout_plan:
            # Return stored workout plan
            return APIResponse(
                success=True,
                message="Workout plan retrieved successfully",
                data={
                    "plan": {
                        "week_plan": workout_plan.week_plan,
                        "goal_type": workout_plan.goal_type,
                        "created_at": workout_plan.created_at.isoformat() if workout_plan.created_at else None,
                        "updated_at": workout_plan.updated_at.isoformat() if workout_plan.updated_at else None
                    },
                    "ai_recommendation": "Here's your personalized workout plan designed to help you achieve your fitness goals. Each day focuses on specific muscle groups to ensure balanced development and proper recovery."
                }
            )
        else:
            # No workout plan exists - generate one using structured JSON plans
            if WORKOUT_PLAN_MANAGER_AVAILABLE:
                try:
                    # Get the user's fitness goal type
                    goal_type = user.fitness_goal_type
                    
                    # Convert JSON plan to week_plan format
                    week_plan = workout_plan_manager.convert_to_week_plan_format(goal_type)
                    
                    # Store the new workout plan
                    db_workout_plan = WorkoutPlan(
                        user_id=user_id,
                        week_plan=week_plan,
                        goal_type=goal_type
                    )
                    db.add(db_workout_plan)
                    await db.commit()
                    await db.refresh(db_workout_plan)
                    
                    return APIResponse(
                        success=True,
                        message="Workout plan generated and stored successfully",
                        data={
                            "plan": {
                                "week_plan": week_plan,
                                "goal_type": goal_type,
                                "created_at": db_workout_plan.created_at.isoformat() if db_workout_plan.created_at else None,
                                "updated_at": db_workout_plan.updated_at.isoformat() if db_workout_plan.updated_at else None
                            },
                            "ai_recommendation": f"I've created a personalized workout plan for your {goal_type.replace('_', ' ')} goals! This evidence-based plan is designed to help you achieve optimal results with proper progression and recovery."
                        }
                    )
                    
                except Exception as e:
                    print(f"Error generating structured workout plan: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to generate workout plan. Please try again later."
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Workout plan generation not available."
                )
            
    except Exception as e:
        print(f"Error in workout plan endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 

@router.get("/plan-full/{user_id}", response_model=APIResponse)
async def get_full_workout_plan(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get full workout plan data including nutrition, rules, and guidelines"""
    try:
        # Get user data
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not WORKOUT_PLAN_MANAGER_AVAILABLE:
            raise HTTPException(status_code=500, detail="Workout plan manager not available")
        
        goal_type = user.fitness_goal_type
        plan = workout_plan_manager.get_plan(goal_type)
        
        if not plan:
            raise HTTPException(status_code=404, detail=f"No workout plan found for goal type: {goal_type}")
        
        # Calculate nutrition targets based on user weight
        nutrition_targets = workout_plan_manager.calculate_nutrition_targets(goal_type, user.weight)
        
        # Transform nutrition data for iOS app compatibility with weight-based conversions
        nutrition_data = plan.get("nutrition", {})
        
        # Convert supplements from string to array if needed, then apply weight conversions
        supplements = nutrition_data.get("supplements", [])
        if isinstance(supplements, str):
            supplements = [s.strip() for s in supplements.split('\n') if s.strip()]
        supplements = workout_plan_manager._convert_weight_based_text(supplements, user.weight)
        
        # Convert timing data and apply weight conversions
        timing = nutrition_data.get("timing_and_training_day_setup", [])
        if isinstance(timing, str):
            timing = [t.strip() for t in timing.split('\n') if t.strip()]
        timing = workout_plan_manager._convert_weight_based_text(timing, user.weight)
        
        # Transform hydration data and apply weight conversions
        hydration = nutrition_data.get("hydration_and_electrolytes", {})
        if isinstance(hydration, dict):
            hydration_list = []
            for key, value in hydration.items():
                if isinstance(value, str):
                    hydration_list.append(f"{key}: {value}")
                else:
                    hydration_list.append(f"{key}: {str(value)}")
            hydration = hydration_list
        hydration = workout_plan_manager._convert_weight_based_text(hydration, user.weight)
        
        # Apply weight conversions to other nutrition fields
        goal = workout_plan_manager._convert_weight_based_text(nutrition_data.get("goal", ""), user.weight)
        calories = workout_plan_manager._convert_weight_based_text(nutrition_data.get("calories", ""), user.weight)
        protein = workout_plan_manager._convert_weight_based_text(nutrition_data.get("protein", ""), user.weight)
        carbohydrate = workout_plan_manager._convert_weight_based_text(nutrition_data.get("carbohydrate", ""), user.weight)
        fat = workout_plan_manager._convert_weight_based_text(nutrition_data.get("fat", ""), user.weight)
        
        # Create iOS-compatible nutrition structure
        ios_nutrition = {
            "goal": goal,
            "calories": calories,
            "protein": protein,
            "carbohydrate": carbohydrate,
            "fat": fat,
            "supplements": supplements,
            "hydration_and_electrolytes": hydration,
            "timing": timing
        }
        
        return APIResponse(
            success=True,
            message="Full workout plan retrieved successfully",
            data={
                "overview": plan.get("overview", ""),
                "weekly_split": plan.get("weekly_split", []),
                "global_rules": plan.get("global_rules", []),
                "days": plan.get("days", {}),
                "conditioning_and_recovery": plan.get("conditioning_and_recovery", []),
                "nutrition": ios_nutrition,
                "nutrition_targets": nutrition_targets,
                "execution_checklist": plan.get("execution_checklist", []),
                "goal_type": goal_type
            }
        )
        
    except Exception as e:
        print(f"Error in full workout plan endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 

@router.get("/plans/discover", response_model=APIResponse)
async def discover_workout_plans(
    category: str = None,
    difficulty: str = None,
    plan_type: str = None,
    limit: int = 20
):
    """Discover available workout plans with rich metadata for frontend display"""
    try:
        # Import WorkoutPlanService here to avoid circular imports
        from ..services.workout_plan_service import WorkoutPlanService
        
        workout_service = WorkoutPlanService()
        
        # Get all plans from database
        db_plans = {}
        try:
            db_plans = await workout_service.get_all_plans()
        except Exception as e:
            print(f"⚠️ Could not load plans from database: {e}")
            db_plans = {}
        
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
            try:
                metadata = await workout_service.get_plan_metadata(plan_id)
                if metadata:
                    all_plans[plan_id] = {
                        "plan_data": plan_data,
                        "metadata": metadata["metadata"],
                        "created_at": metadata["created_at"],
                        "updated_at": metadata["updated_at"],
                        "source": "database"
                    }
            except Exception as e:
                print(f"⚠️ Could not get metadata for plan {plan_id}: {e}")
        
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
                "total_plans": len(plans_for_frontend),
                "filters_applied": {
                    "category": category,
                    "difficulty": difficulty,
                    "plan_type": plan_type,
                    "limit": limit
                }
            }
        )
        
    except Exception as e:
        print(f"Error in workout plan discovery: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/plans/categories", response_model=APIResponse)
async def get_workout_plan_categories():
    """Get all available workout plan categories"""
    try:
        # Import WorkoutPlanService here to avoid circular imports
        from ..services.workout_plan_service import WorkoutPlanService
        
        workout_service = WorkoutPlanService()
        
        # Get categories from database
        db_categories = set()
        try:
            db_plans = await workout_service.get_all_plans()
            for plan_id, plan_data in db_plans.items():
                metadata = await workout_service.get_plan_metadata(plan_id)
                if metadata and "metadata" in metadata:
                    category = metadata["metadata"].get("category")
                    if category:
                        db_categories.add(category)
        except Exception as e:
            print(f"⚠️ Could not load categories from database: {e}")
        
        # Get categories from JSON file
        json_categories = set()
        try:
            with open("app/data/workout_plans.json", "r") as f:
                json_plans = json.load(f)
                for plan_id, plan_data in json_plans.items():
                    # Default categories for JSON plans
                    json_categories.add("general")
        except FileNotFoundError:
            pass
        
        # Combine all categories
        all_categories = list(db_categories.union(json_categories))
        
        return APIResponse(
            success=True,
            message="Workout plan categories retrieved successfully",
            data={
                "categories": all_categories,
                "total_categories": len(all_categories)
            }
        )
        
    except Exception as e:
        print(f"Error getting workout plan categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/plans/difficulties", response_model=APIResponse)
async def get_workout_plan_difficulties():
    """Get all available workout plan difficulties"""
    try:
        # Import WorkoutPlanService here to avoid circular imports
        from ..services.workout_plan_service import WorkoutPlanService
        
        workout_service = WorkoutPlanService()
        
        # Get difficulties from database
        db_difficulties = set()
        try:
            db_plans = await workout_service.get_all_plans()
            for plan_id, plan_data in db_plans.items():
                metadata = await workout_service.get_plan_metadata(plan_id)
                if metadata and "metadata" in metadata:
                    difficulty = metadata["metadata"].get("difficulty")
                    if difficulty:
                        db_difficulties.add(difficulty)
        except Exception as e:
            print(f"⚠️ Could not load difficulties from database: {e}")
        
        # Get difficulties from JSON file
        json_difficulties = set()
        try:
            with open("app/data/workout_plans.json", "r") as f:
                json_plans = json.load(f)
                for plan_id, plan_data in json_plans.items():
                    # Default difficulties for JSON plans
                    json_difficulties.add("intermediate")
        except FileNotFoundError:
            pass
        
        # Combine all difficulties
        all_difficulties = list(db_difficulties.union(json_difficulties))
        
        return APIResponse(
            success=True,
            message="Workout plan difficulties retrieved successfully",
            data={
                "difficulties": all_difficulties,
                "total_difficulties": len(all_difficulties)
            }
        )
        
    except Exception as e:
        print(f"Error getting workout plan difficulties: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 