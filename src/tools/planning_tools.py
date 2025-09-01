import asyncio
from typing import List, Dict, Any
from src.tools.base_tool import BaseTool
from src.utils.config import Config
import openai

class ExerciseDatabaseTool(BaseTool):
    """Tool for selecting appropriate exercises based on criteria."""
    
    def __init__(self):
        super().__init__(
            name="exercise_database",
            description="Select appropriate exercises based on category, difficulty, and equipment"
        )
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Exercise database
        self.exercises = {
            "core": {
                "beginner": [
                    {"name": "Pelvic tilts", "equipment": [], "sets": "3", "reps": "10-15", "rest": "60s"},
                    {"name": "Dead bug", "equipment": [], "sets": "3", "reps": "8-12", "rest": "60s"},
                    {"name": "Bird dog", "equipment": [], "sets": "3", "reps": "8-12", "rest": "60s"}
                ],
                "intermediate": [
                    {"name": "Plank", "equipment": [], "sets": "3", "reps": "30-60s", "rest": "60s"},
                    {"name": "Side plank", "equipment": [], "sets": "3", "reps": "20-30s", "rest": "60s"}
                ]
            },
            "pelvic_floor": {
                "beginner": [
                    {"name": "Kegel exercises", "equipment": [], "sets": "3", "reps": "10", "rest": "60s"},
                    {"name": "Pelvic floor activation", "equipment": [], "sets": "3", "reps": "5-10", "rest": "60s"}
                ]
            },
            "strength": {
                "beginner": [
                    {"name": "Bodyweight squats", "equipment": [], "sets": "3", "reps": "10-15", "rest": "90s"},
                    {"name": "Push-ups (modified)", "equipment": [], "sets": "3", "reps": "5-10", "rest": "90s"}
                ]
            }
        }
    
    async def execute(self, category: str, difficulty: str, equipment: List[str] = None) -> List[Dict[str, Any]]:
        """Select exercises based on criteria."""
        
        if equipment is None:
            equipment = []
        
        # Get exercises from database
        available_exercises = self.exercises.get(category, {}).get(difficulty, [])
        
        # Filter by equipment if specified
        if equipment:
            filtered_exercises = [
                ex for ex in available_exercises 
                if not ex["equipment"] or all(eq in equipment for eq in ex["equipment"])
            ]
        else:
            filtered_exercises = available_exercises
        
        # If no exercises found, use AI to generate suggestions
        if not filtered_exercises:
            return await self._generate_exercises(category, difficulty, equipment)
        
        return filtered_exercises
    
    async def _generate_exercises(self, category: str, difficulty: str, equipment: List[str]) -> List[Dict[str, Any]]:
        """Generate exercises using AI when database doesn't have matches."""
        
        prompt = f"""
        Generate 3-5 {difficulty} level exercises for {category} training.
        Available equipment: {equipment if equipment else 'bodyweight only'}
        
        For each exercise, provide:
        - Exercise name
        - Equipment needed
        - Sets and reps
        - Rest period
        - Brief description
        
        Format as JSON array.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=Config.TEMPERATURE
            )
            
            # Parse response (simplified for demo)
            return [
                {
                    "name": f"AI Generated {category} exercise",
                    "equipment": equipment,
                    "sets": "3",
                    "reps": "10-15",
                    "rest": "60s",
                    "notes": "AI generated exercise"
                }
            ]
        except Exception as e:
            return []

class ProgressionModelTool(BaseTool):
    """Tool for designing progressive overload schemes."""
    
    def __init__(self):
        super().__init__(
            name="progression_model",
            description="Design progressive overload schemes for different training goals"
        )
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def execute(self, goal: str, timeline: str, starting_level: str) -> Dict[str, Any]:
        """Design progression model."""
        
        progression_models = {
            "core_restoration": {
                "phase_1": {"weeks": "1-4", "focus": "Foundation", "intensity": "Low", "volume": "Low"},
                "phase_2": {"weeks": "5-8", "focus": "Progressive", "intensity": "Moderate", "volume": "Moderate"},
                "phase_3": {"weeks": "9-12", "focus": "Integration", "intensity": "Moderate-High", "volume": "Moderate-High"}
            },
            "strength_improvement": {
                "phase_1": {"weeks": "1-4", "focus": "Technique", "intensity": "Moderate", "volume": "High"},
                "phase_2": {"weeks": "5-8", "focus": "Strength", "intensity": "High", "volume": "Moderate"},
                "phase_3": {"weeks": "9-12", "focus": "Peak", "intensity": "Very High", "volume": "Low"}
            }
        }
        
        return progression_models.get(goal, {
            "phase_1": {"weeks": "1-4", "focus": "Foundation", "intensity": "Low", "volume": "Low"},
            "phase_2": {"weeks": "5-8", "focus": "Progressive", "intensity": "Moderate", "volume": "Moderate"},
            "phase_3": {"weeks": "9-12", "focus": "Advanced", "intensity": "Moderate-High", "volume": "Moderate-High"}
        })

class NutritionCalculatorTool(BaseTool):
    """Tool for calculating nutrition requirements."""
    
    def __init__(self):
        super().__init__(
            name="nutrition_calculator",
            description="Calculate nutrition requirements based on goals and activity level"
        )
    
    async def execute(self, goal: str, weight: float, activity_level: str, age: int, gender: str) -> Dict[str, Any]:
        """Calculate nutrition requirements."""
        
        # Basic BMR calculation (Mifflin-St Jeor Equation)
        if gender.lower() == "male":
            bmr = 10 * weight + 6.25 * 170 - 5 * age + 5  # Assuming average height
        else:
            bmr = 10 * weight + 6.25 * 160 - 5 * age - 161  # Assuming average height
        
        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "lightly_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extremely_active": 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.2)
        
        # Adjust for goals
        if goal == "weight_loss":
            calories = tdee * 0.85  # 15% deficit
            protein_multiplier = 2.2  # Higher protein for muscle preservation
        elif goal == "muscle_gain":
            calories = tdee * 1.1  # 10% surplus
            protein_multiplier = 1.8
        else:  # maintenance
            calories = tdee
            protein_multiplier = 1.6
        
        protein = weight * protein_multiplier
        fat = calories * 0.25 / 9  # 25% of calories from fat
        carbs = (calories - (protein * 4) - (fat * 9)) / 4
        
        return {
            "calories": round(calories),
            "protein_g": round(protein),
            "fat_g": round(fat),
            "carbs_g": round(carbs),
            "goal": goal,
            "activity_level": activity_level
        }

