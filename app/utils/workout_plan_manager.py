"""
Workout Plan Manager

Manages loading and accessing structured workout plans from JSON files.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

class WorkoutPlanManager:
    """Manages structured workout plans for different fitness goals"""
    
    def __init__(self):
        self.plans = self._load_workout_plans()
        self.exercise_mapping = self._create_exercise_mapping()
    
    def _load_workout_plans(self) -> Dict[str, Any]:
        """Load workout plans from JSON file"""
        try:
            json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'workout_plans.json')
            with open(json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading workout plans: {e}")
            return {}
    
    def _create_exercise_mapping(self) -> Dict[str, str]:
        """Create mapping from JSON exercise names to database exercise names"""
        return {
            # Building Muscle exercises
            "Barbell bench press": "Bench Press",
            "Incline DB press": "Incline Dumbbell Press",
            "Standing barbell overhead press": "Overhead Press",
            "DB lateral raise": "Lateral Raise",
            "Cable or machine chest fly": "Cable Chest Fly",
            "Cable triceps press-down": "Tricep Pushdown",
            "Weighted pull-ups": "Pull-Up",
            "Chest-supported row": "Barbell Row",
            "Romanian deadlift": "Romanian Deadlift",
            "Rear-delt cable fly": "Rear Delt Fly",
            "Barbell curl": "Bicep Curl",
            "Face pull": "Shoulder Face Pull",
            "Back squat": "Squat",
            "Leg press": "Leg Press",
            "Seated or lying leg curl": "Leg Curl",
            "Walking DB lunge": "Walking Lunge",
            "Standing calf raise": "Standing Calf Raise",
            "Ab wheel or plank": "Plank",
            "Incline barbell bench": "Incline Bench Press",
            "DB shoulder press": "Dumbbell Shoulder Press",
            "Machine or weighted dip": "Tricep Dip",
            "Overhead cable triceps extension": "Overhead Tricep Extension",
            "Barbell row": "Barbell Row",
            "Neutral-grip pulldown": "Lat Pulldown",
            "Seated cable row": "Seated Cable Row",
            "Single-arm DB row": "Dumbbell Row",
            "Rear-delt raise": "Rear Delt Fly",
            "Hammer curl": "Hammer Curl",
            "Front squat or hack squat": "Hack Squat",
            "Hip thrust": "Hip Thrust",
            "Bulgarian split squat": "Bulgarian Split Squat",
            "Leg curl": "Leg Curl",
            "Seated calf raise": "Seated Calf Raise",
            "Hanging leg raise": "Hanging Leg Raise",
            
            # Weight Loss exercises
            "Chest-supported row": "Barbell Row",
            "Lat pulldown or pull-ups": "Lat Pulldown",
            "Dumbbell lateral raise": "Lateral Raise",
            "Barbell or cable curl": "Bicep Curl",
            "Triceps pressdown": "Tricep Pushdown",
            "One-arm dumbbell row": "Dumbbell Row",
            "Machine or weighted dip": "Tricep Dip",
            "Seated cable row": "Seated Cable Row",
            "Rear-delt raise": "Rear Delt Fly",
            "Overhead cable triceps extension": "Overhead Tricep Extension",
            
            # Strength exercises
            "Row variation": "Barbell Row",
            "Hamstring accessory (RDL or curl)": "Leg Curl",
            "Core bracing work": "Plank",
            "Overhead press": "Overhead Press",
            "Bench close-grip or paused": "Close-Grip Bench Press",
            "Upper back pull (pulldown or pull-up)": "Lat Pulldown",
            "Hip hinge accessory": "Romanian Deadlift",
            "Back squat or front squat": "Squat",
            "Competition bench press": "Bench Press",
            "Lunge or split squat": "Walking Lunge",
            "Row or face pull": "Shoulder Face Pull",
            "Triceps accessory": "Tricep Extension",
            "Deadlift variation (pause, tempo, or RDL)": "Romanian Deadlift",
            "Bench secondary (touch-and-go, 2-count pause)": "Bench Press",
            "Barbell or chest-supported row": "Barbell Row",
            "Pull-ups or pulldowns": "Lat Pulldown",
            "Posterior chain accessory": "Romanian Deadlift",
            "Core anti-extension or anti-rotation": "Plank",
            
            # Endurance exercises (strength components)
            "squat or split squat": "Squat",
            "hip hinge": "Romanian Deadlift",
            "push": "Bench Press",
            "pull": "Lat Pulldown",
            "calf or core": "Plank"
        }
    
    def get_plan(self, goal_type: str) -> Optional[Dict[str, Any]]:
        """Get workout plan for a specific goal type"""
        return self.plans.get(goal_type)
    
    def get_overview(self, goal_type: str) -> str:
        """Get overview text for a goal type"""
        plan = self.get_plan(goal_type)
        return plan.get("overview", "") if plan else ""
    
    def get_weekly_split(self, goal_type: str) -> List[str]:
        """Get weekly split for a goal type"""
        plan = self.get_plan(goal_type)
        return plan.get("weekly_split", []) if plan else []
    
    def get_global_rules(self, goal_type: str) -> List[Dict[str, str]]:
        """Get global rules for a goal type"""
        plan = self.get_plan(goal_type)
        return plan.get("global_rules", []) if plan else []
    
    def get_days(self, goal_type: str) -> Dict[str, List[str]]:
        """Get workout days for a goal type"""
        plan = self.get_plan(goal_type)
        return plan.get("days", {}) if plan else {}
    
    def get_conditioning_and_recovery(self, goal_type: str) -> List[str]:
        """Get conditioning and recovery guidelines"""
        plan = self.get_plan(goal_type)
        return plan.get("conditioning_and_recovery", []) if plan else []
    
    def get_nutrition(self, goal_type: str) -> Dict[str, Any]:
        """Get nutrition guidelines for a goal type"""
        plan = self.get_plan(goal_type)
        return plan.get("nutrition", {}) if plan else {}
    
    def get_execution_checklist(self, goal_type: str) -> List[str]:
        """Get execution checklist for a goal type"""
        plan = self.get_plan(goal_type)
        return plan.get("execution_checklist", []) if plan else []
    
    def get_day_exercises(self, goal_type: str, day_name: str) -> List[str]:
        """Get exercises for a specific day"""
        days = self.get_days(goal_type)
        return days.get(day_name, [])
    
    def map_exercise_name(self, json_exercise_name: str) -> str:
        """Map JSON exercise name to database exercise name"""
        # Extract the exercise name from the format "1) Exercise Name — 4×5–8"
        if ")" in json_exercise_name:
            exercise_part = json_exercise_name.split(")")[1].split("—")[0].strip()
        else:
            exercise_part = json_exercise_name
        
        # Try to find exact match first
        if exercise_part in self.exercise_mapping:
            return self.exercise_mapping[exercise_part]
        
        # Try partial matches
        for json_name, db_name in self.exercise_mapping.items():
            if json_name.lower() in exercise_part.lower():
                return db_name
        
        # If no match found, return the original exercise part
        return exercise_part
    
    def convert_to_week_plan_format(self, goal_type: str) -> List[Dict[str, Any]]:
        """Convert JSON plan to week_plan format for database storage"""
        days = self.get_days(goal_type)
        weekly_split = self.get_weekly_split(goal_type)
        
        week_plan = []
        
        for split_item in weekly_split:
            if ":" in split_item:
                day_info = split_item.split(":")
                day_name = day_info[0].strip()
                focus = day_info[1].strip()
                
                # Get exercises for this day
                exercises = []
                if focus in days:
                    exercises = [self.map_exercise_name(ex) for ex in days[focus]]
                
                week_plan.append({
                    "day": day_name,
                    "focus": focus,
                    "exercises": exercises
                })
        
        return week_plan
    
    def calculate_nutrition_targets(self, goal_type: str, weight_kg: float) -> Dict[str, Any]:
        """Calculate nutrition targets based on user weight"""
        nutrition = self.get_nutrition(goal_type)
        if not nutrition:
            return {}
        
        # Handle null weight by using default weight
        if weight_kg is None or weight_kg <= 0:
            weight_kg = 70.0  # Default weight in kg
            print(f"⚠️ User weight not set, using default weight: {weight_kg}kg")
        
        targets = {}
        
        # Calculate protein
        if "protein" in nutrition:
            protein_text = nutrition["protein"]
            if "1.6-2.2" in protein_text or "1.6–2.2" in protein_text:
                protein_min = 1.6 * weight_kg
                protein_max = 2.2 * weight_kg
                targets["protein"] = {
                    "min": round(protein_min, 1),
                    "max": round(protein_max, 1),
                    "target": round((protein_min + protein_max) / 2, 1)
                }
            elif "2.0-2.6" in protein_text or "2.0–2.6" in protein_text:
                protein_min = 2.0 * weight_kg
                protein_max = 2.6 * weight_kg
                targets["protein"] = {
                    "min": round(protein_min, 1),
                    "max": round(protein_max, 1),
                    "target": round((protein_min + protein_max) / 2, 1)
                }
            elif "1.6-2.0" in protein_text or "1.6–2.0" in protein_text:
                protein_min = 1.6 * weight_kg
                protein_max = 2.0 * weight_kg
                targets["protein"] = {
                    "min": round(protein_min, 1),
                    "max": round(protein_max, 1),
                    "target": round((protein_min + protein_max) / 2, 1)
                }
        
        # Calculate carbs
        if "carbohydrate" in nutrition:
            carb_text = nutrition["carbohydrate"]
            if "3-6" in carb_text or "3–6" in carb_text:
                carb_min = 3 * weight_kg
                carb_max = 6 * weight_kg
                targets["carbohydrate"] = {
                    "min": round(carb_min, 1),
                    "max": round(carb_max, 1),
                    "target": round((carb_min + carb_max) / 2, 1)
                }
            elif "2-4" in carb_text or "2–4" in carb_text:
                carb_min = 2 * weight_kg
                carb_max = 4 * weight_kg
                targets["carbohydrate"] = {
                    "min": round(carb_min, 1),
                    "max": round(carb_max, 1),
                    "target": round((carb_min + carb_max) / 2, 1)
                }
            elif "5-8" in carb_text or "5–8" in carb_text:
                carb_min = 5 * weight_kg
                carb_max = 8 * weight_kg
                targets["carbohydrate"] = {
                    "min": round(carb_min, 1),
                    "max": round(carb_max, 1),
                    "target": round((carb_min + carb_max) / 2, 1)
                }
        
        # Calculate fat
        if "fat" in nutrition:
            fat_text = nutrition["fat"]
            if "0.6-1.0" in fat_text or "0.6–1.0" in fat_text:
                fat_min = 0.6 * weight_kg
                fat_max = 1.0 * weight_kg
                targets["fat"] = {
                    "min": round(fat_min, 1),
                    "max": round(fat_max, 1),
                    "target": round((fat_min + fat_max) / 2, 1)
                }
            elif "0.5-0.8" in fat_text or "0.5–0.8" in fat_text:
                fat_min = 0.5 * weight_kg
                fat_max = 0.8 * weight_kg
                targets["fat"] = {
                    "min": round(fat_min, 1),
                    "max": round(fat_max, 1),
                    "target": round((fat_min + fat_max) / 2, 1)
                }
            elif "0.8-1.0" in fat_text or "0.8–1.0" in fat_text:
                fat_min = 0.8 * weight_kg
                fat_max = 1.0 * weight_kg
                targets["fat"] = {
                    "min": round(fat_min, 1),
                    "max": round(fat_max, 1),
                    "target": round((fat_min + fat_max) / 2, 1)
                }
        
        # Add supplements with weight-based conversions
        if "supplements" in nutrition:
            targets["supplements"] = self._convert_weight_based_text(nutrition["supplements"], weight_kg)
        
        # Add hydration with weight-based conversions
        if "hydration_and_electrolytes" in nutrition:
            targets["hydration"] = self._convert_weight_based_text(nutrition["hydration_and_electrolytes"], weight_kg)
        
        return targets
    
    def _convert_weight_based_text(self, text_data, weight_kg: float) -> Any:
        """Convert weight-based measurements (g/kg, mg/kg, etc.) to absolute values"""
        if isinstance(text_data, str):
            return self._convert_single_text(text_data, weight_kg)
        elif isinstance(text_data, list):
            return [self._convert_single_text(item, weight_kg) if isinstance(item, str) else item for item in text_data]
        elif isinstance(text_data, dict):
            converted_dict = {}
            for key, value in text_data.items():
                if isinstance(value, str):
                    converted_dict[key] = self._convert_single_text(value, weight_kg)
                else:
                    converted_dict[key] = value
            return converted_dict
        else:
            return text_data
    
    def _convert_single_text(self, text: str, weight_kg: float) -> str:
        """Convert a single text string containing weight-based measurements"""
        import re
        
        # Pattern to match various weight-based measurements
        patterns = [
            # g/kg patterns (e.g., "0.5-1.0 g/kg", "1.6–2.2 g/kg")
            (r'(\d+\.?\d*)-(\d+\.?\d*)\s*g/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}g"),
            (r'(\d+\.?\d*)–(\d+\.?\d*)\s*g/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}g"),
            (r'(\d+\.?\d*)\s*g/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}g"),
            
            # mg/kg patterns (e.g., "1-3 mg/kg", "1–3 mg/kg")
            (r'(\d+\.?\d*)-(\d+\.?\d*)\s*mg/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}mg"),
            (r'(\d+\.?\d*)–(\d+\.?\d*)\s*mg/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}mg"),
            (r'(\d+\.?\d*)\s*mg/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}mg"),
            
            # mg/kg/day patterns
            (r'(\d+\.?\d*)-(\d+\.?\d*)\s*mg/kg/day', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}mg/day"),
            (r'(\d+\.?\d*)–(\d+\.?\d*)\s*mg/kg/day', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}mg/day"),
            (r'(\d+\.?\d*)\s*mg/kg/day', lambda m: f"{int(float(m.group(1)) * weight_kg)}mg/day"),
            
            # ml/kg patterns (e.g., "30-40 ml/kg")
            (r'(\d+\.?\d*)-(\d+\.?\d*)\s*ml/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}ml"),
            (r'(\d+\.?\d*)–(\d+\.?\d*)\s*ml/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}-{int(float(m.group(2)) * weight_kg)}ml"),
            (r'(\d+\.?\d*)\s*ml/kg', lambda m: f"{int(float(m.group(1)) * weight_kg)}ml"),
        ]
        
        converted_text = text
        for pattern, replacement_func in patterns:
            converted_text = re.sub(pattern, replacement_func, converted_text)
        
        return converted_text

# Global instance
workout_plan_manager = WorkoutPlanManager() 