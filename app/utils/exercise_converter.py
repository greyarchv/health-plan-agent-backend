"""
Exercise Converter

Maps workout plan exercises to database exercises and ensures all exercises exist in the database.
This provides a 1:1 mapping between workout plans and the database for consistent exercise tracking.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..models import Exercise, ExerciseData


class ExerciseConverter:
    def __init__(self):
        # Mapping from workout plan exercise names to database exercise names
        # This ensures 1:1 mapping between plan and database
        self.exercise_mapping = {
            # Push A exercises
            "Barbell bench press": "Bench Press",
            "Incline DB press": "Incline Dumbbell Press", 
            "Standing barbell overhead press": "Overhead Press",
            "DB lateral raise": "Lateral Raise",
            "Cable or machine chest fly": "Cable Chest Fly",
            "Cable triceps press-down": "Tricep Pushdown",
            
            # Pull A exercises
            "Weighted pull-ups (or heavy lat pulldown)": "Pull-Up",
            "Chest-supported row": "Barbell Row",
            "Romanian deadlift": "Romanian Deadlift",
            "Rear-delt cable fly": "Rear Delt Fly",
            "Barbell curl": "Bicep Curl",
            "Face pull": "Shoulder Face Pull",
            
            # Legs A exercises
            "Back squat": "Squat",
            "Leg press": "Leg Press",
            "Seated or lying leg curl": "Leg Curl",
            "Walking DB lunge": "Walking Lunge",
            "Standing calf raise": "Standing Calf Raise",
            "Ab wheel or plank": "Plank",
            
            # Push B exercises
            "Incline barbell bench": "Incline Bench Press",
            "DB shoulder press": "Dumbbell Shoulder Press",
            "Machine or weighted dip": "Tricep Dip",
            "DB lateral raise (slow eccentric)": "Lateral Raise",
            "Overhead cable triceps extension": "Overhead Tricep Extension",
            
            # Pull B exercises
            "Barbell row (hips just above parallel)": "Barbell Row",
            "Neutral-grip pulldown": "Lat Pulldown",
            "Seated cable row": "Seated Cable Row",
            "Single-arm DB row": "Dumbbell Row",
            "Rear-delt raise": "Rear Delt Fly",
            "Hammer curl": "Hammer Curl",
            
            # Legs B exercises
            "Front squat or hack squat": "Hack Squat",
            "Hip thrust": "Hip Thrust",
            "Bulgarian split squat": "Bulgarian Split Squat",
            "Leg curl": "Leg Curl",
            "Seated calf raise": "Seated Calf Raise",
            "Hanging leg raise": "Hanging Leg Raise"
        }
        
        # Reverse mapping for database to plan
        self.reverse_mapping = {v: k for k, v in self.exercise_mapping.items()}
    
    def plan_to_database(self, plan_exercise: str) -> str:
        """
        Convert workout plan exercise name to database exercise name.
        
        Args:
            plan_exercise: Exercise name from workout plan (e.g., "Barbell bench press")
            
        Returns:
            Database exercise name (e.g., "Bench Press")
        """
        return self.exercise_mapping.get(plan_exercise, plan_exercise)
    
    def database_to_plan(self, db_exercise: str) -> str:
        """
        Convert database exercise name to workout plan exercise name.
        
        Args:
            db_exercise: Exercise name from database (e.g., "Bench Press")
            
        Returns:
            Plan exercise name (e.g., "Barbell bench press")
        """
        return self.reverse_mapping.get(db_exercise, db_exercise)
    
    def extract_plan_exercise_name(self, exercise_string: str) -> str:
        """
        Extract exercise name from workout plan format.
        
        Args:
            exercise_string: Full exercise string (e.g., "1) Barbell bench press — 4×5–8")
            
        Returns:
            Exercise name (e.g., "Barbell bench press")
        """
        # Remove number and closing parenthesis
        without_number = exercise_string.split(") ", 1)[1] if ") " in exercise_string else exercise_string
        # Remove sets/reps part
        exercise_name = without_number.split(" — ")[0] if " — " in without_number else without_number
        return exercise_name.strip()
    
    def get_database_exercise_name(self, exercise_string: str) -> str:
        """
        Get database exercise name from workout plan exercise string.
        
        Args:
            exercise_string: Full exercise string (e.g., "1) Barbell bench press — 4×5–8")
            
        Returns:
            Database exercise name (e.g., "Bench Press")
        """
        plan_exercise = self.extract_plan_exercise_name(exercise_string)
        return self.plan_to_database(plan_exercise)
    
    async def ensure_exercises_exist(self, db: AsyncSession) -> List[str]:
        """
        Ensure all exercises in the mapping exist in the database.
        Creates any missing exercises.
        
        Args:
            db: Database session
            
        Returns:
            List of exercise names that were created
        """
        created_exercises = []
        
        # Get all existing exercises from database
        result = await db.execute(text("SELECT name FROM exercises"))
        existing_exercises = {row.name for row in result.fetchall()}
        
        # Check which exercises need to be created
        for db_exercise_name in self.exercise_mapping.values():
            if db_exercise_name not in existing_exercises:
                # Create the exercise
                new_exercise = Exercise(
                    name=db_exercise_name,
                    category=self._get_exercise_category(db_exercise_name),
                    description=f"Exercise: {db_exercise_name}",
                    muscle_groups=self._get_muscle_groups(db_exercise_name)
                )
                db.add(new_exercise)
                created_exercises.append(db_exercise_name)
        
        if created_exercises:
            await db.commit()
            print(f"Created {len(created_exercises)} new exercises: {created_exercises}")
        
        return created_exercises
    
    def _get_exercise_category(self, exercise_name: str) -> str:
        """Get exercise category based on exercise name."""
        exercise_lower = exercise_name.lower()
        
        if any(word in exercise_lower for word in ['bench', 'press', 'dip', 'fly']):
            return 'push'
        elif any(word in exercise_lower for word in ['row', 'pull', 'curl', 'face pull']):
            return 'pull'
        elif any(word in exercise_lower for word in ['squat', 'leg', 'calf', 'lunge', 'thrust']):
            return 'legs'
        elif any(word in exercise_lower for word in ['plank', 'ab', 'leg raise']):
            return 'core'
        else:
            return 'other'
    
    def _get_muscle_groups(self, exercise_name: str) -> List[str]:
        """Get muscle groups for an exercise."""
        exercise_lower = exercise_name.lower()
        muscle_groups = []
        
        if any(word in exercise_lower for word in ['bench', 'chest', 'fly']):
            muscle_groups.append('chest')
        if any(word in exercise_lower for word in ['press', 'shoulder', 'lateral', 'overhead']):
            muscle_groups.append('shoulders')
        if any(word in exercise_lower for word in ['tricep', 'dip', 'extension']):
            muscle_groups.append('triceps')
        if any(word in exercise_lower for word in ['row', 'pull', 'lat']):
            muscle_groups.append('back')
        if any(word in exercise_lower for word in ['curl', 'bicep']):
            muscle_groups.append('biceps')
        if any(word in exercise_lower for word in ['squat', 'leg press', 'hack']):
            muscle_groups.append('quadriceps')
        if any(word in exercise_lower for word in ['deadlift', 'leg curl']):
            muscle_groups.append('hamstrings')
        if any(word in exercise_lower for word in ['calf']):
            muscle_groups.append('calves')
        if any(word in exercise_lower for word in ['lunge', 'split']):
            muscle_groups.append('glutes')
        if any(word in exercise_lower for word in ['plank', 'ab', 'leg raise']):
            muscle_groups.append('core')
        
        return muscle_groups if muscle_groups else ['general']
    
    def get_exercise_type(self, exercise_name: str) -> str:
        """
        Determine if an exercise is compound or isolation.
        
        Args:
            exercise_name: Exercise name (can be plan or database format)
            
        Returns:
            'compound' or 'isolation'
        """
        # First convert to database format if it's a plan exercise
        db_exercise = self.get_database_exercise_name(exercise_name) if " — " in exercise_name else exercise_name
        exercise_lower = db_exercise.lower()
        
        # Compound exercises (multi-joint, multiple muscle groups)
        compound_exercises = [
            'bench press', 'incline bench press', 'overhead press', 'dumbbell shoulder press',
            'pull-up', 'barbell row', 'seated cable row', 'dumbbell row',
            'squat', 'front squat', 'hack squat', 'leg press',
            'deadlift', 'romanian deadlift', 'hip thrust',
            'dip', 'tricep dip', 'bulgarian split squat', 'walking lunge'
        ]
        
        # Check if it's a compound exercise
        for compound in compound_exercises:
            if compound in exercise_lower:
                return 'compound'
        
        # Isolation exercises (single-joint, single muscle group focus)
        isolation_exercises = [
            'lateral raise', 'rear delt fly', 'face pull', 'rear delt raise',
            'bicep curl', 'hammer curl', 'tricep pushdown', 'overhead tricep extension',
            'cable chest fly', 'leg curl', 'standing calf raise', 'seated calf raise',
            'plank', 'hanging leg raise', 'ab wheel'
        ]
        
        # Check if it's an isolation exercise
        for isolation in isolation_exercises:
            if isolation in exercise_lower:
                return 'isolation'
        
        # Default to compound if uncertain
        return 'compound'
    
    def get_rest_time(self, exercise_name: str) -> int:
        """
        Get recommended rest time for an exercise.
        
        Args:
            exercise_name: Exercise name (can be plan or database format)
            
        Returns:
            Rest time in seconds
        """
        exercise_type = self.get_exercise_type(exercise_name)
        return 120 if exercise_type == 'compound' else 75  # 2 minutes for compound, 75 seconds for isolation


# Global instance
exercise_converter = ExerciseConverter()
