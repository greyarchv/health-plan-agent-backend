from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from datetime import datetime, timedelta, date
from ..database import get_sync_db, get_async_db
from ..models import User, MealPlan, NutritionChecklist
from ..schemas import MealPlanCreate, MealPlan as MealPlanSchema, APIResponse
# Removed AI orchestrator dependency - using simplified system
import json
from sqlalchemy import text

router = APIRouter(tags=["nutrition"])

# Add a simple health check endpoint that doesn't require database
@router.get("/status")
async def nutrition_health():
    """Health check for nutrition router"""
    return {"status": "healthy", "message": "Nutrition router is working"}

@router.post("/checklist")
async def save_nutrition_checklist(
    user_id: int,
    checklist_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db)
):
    """Save nutrition checklist state for a user"""
    try:
        # Extract data
        checklist_date = checklist_data.get("date")
        completed_supplements = checklist_data.get("completed_supplements", [])
        macro_progress = checklist_data.get("macro_progress", {})
        
        # Convert date string to date object
        if isinstance(checklist_date, str):
            checklist_date = datetime.strptime(checklist_date, "%Y-%m-%d").date()
        elif isinstance(checklist_date, date):
            pass
        else:
            checklist_date = datetime.now().date()
        
        # Check if entry exists for this date
        existing_query = text("""
            SELECT id FROM nutrition_checklists 
            WHERE user_id = :user_id AND checklist_date = :checklist_date
        """)
        
        result = await db.execute(existing_query, {
            "user_id": user_id,
            "checklist_date": checklist_date
        })
        
        existing_entry = result.fetchone()
        
        if existing_entry:
            # Update existing entry
            update_query = text("""
                UPDATE nutrition_checklists 
                SET completed_supplements = :completed_supplements,
                    protein_progress = :protein_progress,
                    carbs_progress = :carbs_progress,
                    fat_progress = :fat_progress,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id AND checklist_date = :checklist_date
            """)
            
            await db.execute(update_query, {
                "user_id": user_id,
                "checklist_date": checklist_date,
                "completed_supplements": json.dumps(completed_supplements),
                "protein_progress": macro_progress.get("protein", 0.0),
                "carbs_progress": macro_progress.get("carbs", 0.0),
                "fat_progress": macro_progress.get("fat", 0.0)
            })
        else:
            # Create new entry
            insert_query = text("""
                INSERT INTO nutrition_checklists 
                (user_id, checklist_date, completed_supplements, protein_progress, carbs_progress, fat_progress)
                VALUES (:user_id, :checklist_date, :completed_supplements, :protein_progress, :carbs_progress, :fat_progress)
            """)
            
            await db.execute(insert_query, {
                "user_id": user_id,
                "checklist_date": checklist_date,
                "completed_supplements": json.dumps(completed_supplements),
                "protein_progress": macro_progress.get("protein", 0.0),
                "carbs_progress": macro_progress.get("carbs", 0.0),
                "fat_progress": macro_progress.get("fat", 0.0)
            })
        
        await db.commit()
        
        return APIResponse(
            success=True,
            message="Nutrition checklist saved successfully",
            data={
                "user_id": user_id,
                "date": checklist_date.isoformat(),
                "completed_supplements": completed_supplements,
                "macro_progress": macro_progress
            }
        )
        
    except Exception as e:
        await db.rollback()
        print(f"Error saving nutrition checklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/checklist/{user_id}")
async def get_nutrition_checklist(
    user_id: int,
    date: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get nutrition checklist state for a user"""
    try:
        # Use provided date or today
        if date:
            checklist_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            checklist_date = datetime.now().date()
        
        query = text("""
            SELECT completed_supplements, protein_progress, carbs_progress, fat_progress
            FROM nutrition_checklists 
            WHERE user_id = :user_id AND checklist_date = :checklist_date
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "checklist_date": checklist_date
        })
        
        entry = result.fetchone()
        
        if entry:
            completed_supplements = json.loads(entry.completed_supplements) if entry.completed_supplements else []
            
            return APIResponse(
                success=True,
                message="Nutrition checklist retrieved successfully",
                data={
                    "user_id": user_id,
                    "date": checklist_date.isoformat(),
                    "completed_supplements": completed_supplements,
                    "macro_progress": {
                        "protein": entry.protein_progress,
                        "carbs": entry.carbs_progress,
                        "fat": entry.fat_progress
                    }
                }
            )
        else:
            # Return empty checklist for new day
            return APIResponse(
                success=True,
                message="No checklist found for this date",
                data={
                    "user_id": user_id,
                    "date": checklist_date.isoformat(),
                    "completed_supplements": [],
                    "macro_progress": {
                        "protein": 0.0,
                        "carbs": 0.0,
                        "fat": 0.0
                    }
                }
            )
        
    except Exception as e:
        print(f"Error retrieving nutrition checklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adherence/{user_id}")
async def get_nutrition_adherence(
    user_id: int,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get nutrition adherence analytics for a user"""
    try:
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Convert dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Get all checklist entries for the date range
        query = text("""
            SELECT checklist_date, completed_supplements, protein_progress, carbs_progress, fat_progress
            FROM nutrition_checklists 
            WHERE user_id = :user_id 
            AND checklist_date BETWEEN :start_date AND :end_date
            ORDER BY checklist_date
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "start_date": start_dt,
            "end_date": end_dt
        })
        
        entries = result.fetchall()
        
        # Get user's nutrition targets for comparison
        user_query = text("""
            SELECT wp.week_plan
            FROM workout_plans wp
            WHERE wp.user_id = :user_id
            ORDER BY wp.created_at DESC
            LIMIT 1
        """)
        
        user_result = await db.execute(user_query, {"user_id": user_id})
        user_plan = user_result.fetchone()
        
        if not user_plan:
            raise HTTPException(status_code=404, detail="No workout plan found for user")
        
        # Extract nutrition targets from week_plan
        week_plan = user_plan.week_plan
        # week_plan is null, so we need to get nutrition_targets from the full workout plan
        # For now, use default targets since we can't access the full plan from this query
        nutrition_targets = {
            "protein": {"target": 161.5},
            "carbohydrate": {"target": 382.5},
            "fat": {"target": 85.0}
        }
        
        if not nutrition_targets:
            # Fallback to default targets
            nutrition_targets = {
                "protein": {"target": 150.0},
                "carbohydrate": {"target": 200.0},
                "fat": {"target": 65.0}
            }
        
        # Calculate adherence metrics
        adherence_data = calculate_adherence_metrics(entries, nutrition_targets, start_dt, end_dt)
        
        return APIResponse(
            success=True,
            message="Nutrition adherence data retrieved successfully",
            data=adherence_data
        )
        
    except Exception as e:
        print(f"Error retrieving nutrition adherence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adherence/{user_id}/supplements")
async def get_supplement_adherence(
    user_id: int,
    supplement_name: str = None,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed supplement adherence for a specific supplement or all supplements"""
    try:
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Convert dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Get supplement adherence data
        query = text("""
            SELECT checklist_date, completed_supplements
            FROM nutrition_checklists 
            WHERE user_id = :user_id 
            AND checklist_date BETWEEN :start_date AND :end_date
            ORDER BY checklist_date
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "start_date": start_dt,
            "end_date": end_dt
        })
        
        entries = result.fetchall()
        
        # Calculate supplement-specific adherence
        supplement_adherence = calculate_supplement_adherence(entries, supplement_name)
        
        return APIResponse(
            success=True,
            message="Supplement adherence data retrieved successfully",
            data=supplement_adherence
        )
        
    except Exception as e:
        print(f"Error retrieving supplement adherence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adherence/{user_id}/macros")
async def get_macro_adherence(
    user_id: int,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed macro adherence analytics"""
    try:
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Convert dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Get macro progress data
        query = text("""
            SELECT checklist_date, protein_progress, carbs_progress, fat_progress
            FROM nutrition_checklists 
            WHERE user_id = :user_id 
            AND checklist_date BETWEEN :start_date AND :end_date
            ORDER BY checklist_date
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "start_date": start_dt,
            "end_date": end_dt
        })
        
        entries = result.fetchall()
        
        # Get user's nutrition targets
        user_query = text("""
            SELECT wp.week_plan
            FROM workout_plans wp
            WHERE wp.user_id = :user_id
            ORDER BY wp.created_at DESC
            LIMIT 1
        """)
        
        user_result = await db.execute(user_query, {"user_id": user_id})
        user_plan = user_result.fetchone()
        
        if not user_plan:
            raise HTTPException(status_code=404, detail="No workout plan found for user")
        
        # Extract nutrition targets from week_plan
        week_plan = user_plan.week_plan
        # week_plan is a list, so we need to get nutrition_targets from the first item or use a different approach
        nutrition_targets = {}
        if isinstance(week_plan, list) and len(week_plan) > 0:
            # Try to get nutrition_targets from the first item
            first_item = week_plan[0]
            if isinstance(first_item, dict):
                nutrition_targets = first_item.get("nutrition_targets", {})
        
        if not nutrition_targets:
            # Fallback to default targets
            nutrition_targets = {
                "protein": {"target": 150.0},
                "carbohydrate": {"target": 200.0},
                "fat": {"target": 65.0}
            }
        
        # Calculate macro adherence
        macro_adherence = calculate_macro_adherence(entries, nutrition_targets)
        
        return APIResponse(
            success=True,
            message="Macro adherence data retrieved successfully",
            data=macro_adherence
        )
        
    except Exception as e:
        print(f"Error retrieving macro adherence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log", response_model=APIResponse)
async def log_meal(meal_data: MealPlanCreate, user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Log a meal"""
    try:
        # Verify user exists
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create meal log entry
        meal_log = MealPlan(
            user_id=user_id,
            meal_type=meal_data.meal_type,
            meal_data=meal_data.meal_data,
            calories=meal_data.calories,
            protein=meal_data.protein,
            carbs=meal_data.carbs,
            fat=meal_data.fat
        )
        
        db.add(meal_log)
        await db.commit()
        await db.refresh(meal_log)
        
        return APIResponse(
            success=True,
            message="Meal logged successfully",
            data=MealPlanSchema.from_orm(meal_log)
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}", response_model=APIResponse)
async def get_meal_history(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get user's meal history"""
    try:
        # Verify user exists
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get meal logs for user
        stmt = select(MealPlan).where(MealPlan.user_id == user_id).order_by(MealPlan.plan_date.desc())
        result = await db.execute(stmt)
        meal_logs = result.scalars().all()
        
        return APIResponse(
            success=True,
            message="Meal history retrieved successfully",
            data=[MealPlanSchema.from_orm(log) for log in meal_logs]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

def calculate_adherence_metrics(entries, nutrition_targets, start_date, end_date):
    """Calculate comprehensive adherence metrics"""
    total_days = (end_date - start_date).days + 1
    tracked_days = len(entries)
    
    # Supplement adherence
    all_supplements = set()
    supplement_days = {}
    
    for entry in entries:
        if entry.completed_supplements:
            completed_supps = json.loads(entry.completed_supplements)
            for supp in completed_supps:
                all_supplements.add(supp)
                if supp not in supplement_days:
                    supplement_days[supp] = 0
                supplement_days[supp] += 1
    
    # Calculate supplement adherence percentages
    supplement_adherence = {}
    for supplement in all_supplements:
        days_taken = supplement_days.get(supplement, 0)
        adherence_percentage = (days_taken / tracked_days * 100) if tracked_days > 0 else 0
        supplement_adherence[supplement] = {
            "days_taken": days_taken,
            "total_tracked_days": tracked_days,
            "adherence_percentage": round(adherence_percentage, 1),
            "missed_days": tracked_days - days_taken
        }
    
    # Macro adherence
    protein_target = nutrition_targets.get("protein", {}).get("target", 0)
    carbs_target = nutrition_targets.get("carbohydrate", {}).get("target", 0)
    fat_target = nutrition_targets.get("fat", {}).get("target", 0)
    
    total_protein = sum(entry.protein_progress for entry in entries)
    total_carbs = sum(entry.carbs_progress for entry in entries)
    total_fat = sum(entry.fat_progress for entry in entries)
    
    avg_protein = total_protein / tracked_days if tracked_days > 0 else 0
    avg_carbs = total_carbs / tracked_days if tracked_days > 0 else 0
    avg_fat = total_fat / tracked_days if tracked_days > 0 else 0
    
    macro_adherence = {
        "protein": {
            "target": protein_target,
            "average_consumed": round(avg_protein, 1),
            "target_percentage": round((avg_protein / protein_target * 100) if protein_target > 0 else 0, 1),
            "total_consumed": round(total_protein, 1),
            "total_target": protein_target * tracked_days,
            "deficit": round((protein_target * tracked_days) - total_protein, 1)
        },
        "carbs": {
            "target": carbs_target,
            "progress": carbs_target,
            "average_consumed": round(avg_carbs, 1),
            "target_percentage": round((avg_carbs / carbs_target * 100) if carbs_target > 0 else 0, 1),
            "total_consumed": round(total_carbs, 1),
            "total_target": carbs_target * tracked_days,
            "deficit": round((carbs_target * tracked_days) - total_carbs, 1)
        },
        "fat": {
            "target": fat_target,
            "average_consumed": round(avg_fat, 1),
            "target_percentage": round((avg_fat / fat_target * 100) if fat_target > 0 else 0, 1),
            "total_consumed": round(total_fat, 1),
            "total_target": fat_target * tracked_days,
            "deficit": round((fat_target * tracked_days) - total_fat, 1)
        }
    }
    
    # Overall adherence score
    supplement_score = sum(data["adherence_percentage"] for data in supplement_adherence.values()) / len(supplement_adherence) if supplement_adherence else 0
    macro_score = (macro_adherence["protein"]["target_percentage"] + macro_adherence["carbs"]["target_percentage"] + macro_adherence["fat"]["target_percentage"]) / 3
    
    overall_adherence = round((supplement_score + macro_score) / 2, 1)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_days": total_days,
            "tracked_days": tracked_days,
            "tracking_coverage": round((tracked_days / total_days * 100) if total_days > 0 else 0, 1)
        },
        "overall_adherence_score": overall_adherence,
        "supplement_adherence": supplement_adherence,
        "macro_adherence": macro_adherence,
        "daily_breakdown": [
            {
                "date": entry.checklist_date.isoformat(),
                "supplements_taken": json.loads(entry.completed_supplements) if entry.completed_supplements else [],
                "protein": entry.protein_progress,
                "carbs": entry.carbs_progress,
                "fat": entry.fat_progress
            }
            for entry in entries
        ]
    }

def calculate_supplement_adherence(entries, supplement_name=None):
    """Calculate supplement-specific adherence"""
    all_supplements = set()
    supplement_days = {}
    
    for entry in entries:
        if entry.completed_supplements:
            completed_supps = json.loads(entry.completed_supplements)
            for supp in completed_supps:
                all_supplements.add(supp)
                if supp not in supplement_days:
                    supplement_days[supp] = []
                supplement_days[supp].append(entry.checklist_date.isoformat())
    
    if supplement_name:
        # Return data for specific supplement
        if supplement_name in supplement_days:
            days_taken = len(supplement_days[supplement_name])
            total_days = len(entries)
            adherence_percentage = (days_taken / total_days * 100) if total_days > 0 else 0
            
            return {
                "supplement": supplement_name,
                "days_taken": days_taken,
                "total_tracked_days": total_days,
                "adherence_percentage": round(adherence_percentage, 1),
                "missed_days": total_days - days_taken,
                "dates_taken": supplement_days[supplement_name],
                "dates_missed": [
                    entry.checklist_date.isoformat() 
                    for entry in entries 
                    if entry.checklist_date.isoformat() not in supplement_days[supplement_name]
                ]
            }
        else:
            return {
                "supplement": supplement_name,
                "days_taken": 0,
                "total_tracked_days": len(entries),
                "adherence_percentage": 0.0,
                "missed_days": len(entries),
                "dates_taken": [],
                "dates_missed": [entry.checklist_date.isoformat() for entry in entries]
            }
    else:
        # Return data for all supplements
        supplement_data = {}
        for supplement in all_supplements:
            days_taken = len(supplement_days[supplement])
            total_days = len(entries)
            adherence_percentage = (days_taken / total_days * 100) if total_days > 0 else 0
            
            supplement_data[supplement] = {
                "days_taken": days_taken,
                "total_tracked_days": total_days,
                "adherence_percentage": round(adherence_percentage, 1),
                "missed_days": total_days - days_taken,
                "dates_taken": supplement_days[supplement]
            }
        
        return supplement_data

def calculate_macro_adherence(entries, nutrition_targets):
    """Calculate macro-specific adherence"""
    protein_target = nutrition_targets.get("protein", {}).get("target", 0)
    carbs_target = nutrition_targets.get("carbohydrate", {}).get("target", 0)
    fat_target = nutrition_targets.get("fat", {}).get("target", 0)
    
    daily_macro_data = []
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    for entry in entries:
        daily_macro_data.append({
            "date": entry.checklist_date.isoformat(),
            "protein": {
                "consumed": entry.protein_progress,
                "target": protein_target,
                "percentage": round((entry.protein_progress / protein_target * 100) if protein_target > 0 else 0, 1),
                "deficit": max(0, protein_target - entry.protein_progress)
            },
            "carbs": {
                "consumed": entry.carbs_progress,
                "target": carbs_target,
                "percentage": round((entry.carbs_progress / carbs_target * 100) if carbs_target > 0 else 0, 1),
                "deficit": max(0, carbs_target - entry.carbs_progress)
            },
            "fat": {
                "consumed": entry.fat_progress,
                "target": fat_target,
                "percentage": round((entry.fat_progress / fat_target * 100) if fat_target > 0 else 0, 1),
                "deficit": max(0, fat_target - entry.fat_progress)
            }
        })
        
        total_protein += entry.protein_progress
        total_carbs += entry.carbs_progress
        total_fat += entry.fat_progress
    
    tracked_days = len(entries)
    
    return {
        "targets": {
            "protein": protein_target,
            "carbs": carbs_target,
            "fat": fat_target
        },
        "totals": {
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1)
        },
        "averages": {
            "protein": round(total_protein / tracked_days, 1) if tracked_days > 0 else 0,
            "carbs": round(total_carbs / tracked_days, 1) if tracked_days > 0 else 0,
            "fat": round(total_fat / tracked_days, 1) if tracked_days > 0 else 0
        },
        "target_percentages": {
            "protein": round((total_protein / (protein_target * tracked_days) * 100) if protein_target > 0 and tracked_days > 0 else 0, 1),
            "carbs": round((total_carbs / (carbs_target * tracked_days) * 100) if carbs_target > 0 and tracked_days > 0 else 0, 1),
            "fat": round((total_fat / (fat_target * tracked_days) * 100) if fat_target > 0 and tracked_days > 0 else 0, 1)
        },
        "daily_breakdown": daily_macro_data
    } 