import asyncio
from typing import List, Dict, Any
from .base_agent import BaseAgent
from ..tools.planning_tools import NutritionCalculatorTool
from ..utils.config import Config
import openai

class NutritionAgent(BaseAgent):
    """Agent responsible for designing nutrition components of health plans."""
    
    def __init__(self):
        super().__init__(
            name="Nutrition Agent",
            description="Creates meal plans, supplementation strategies, and hydration protocols"
        )
        
        # Add nutrition tools
        self.add_tool(NutritionCalculatorTool())
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def process(self, fitness_plan: Dict[str, Any], goals: List[str], 
                     constraints: List[str], preferences: List[str]) -> Dict[str, Any]:
        """Design nutrition component based on fitness plan and requirements."""
        
        nutrition_plan = {
            "goal": "",
            "calories": "",
            "protein": "",
            "carbohydrate": "",
            "fat": "",
            "meal_timing": [],
            "supplements": [],
            "hydration": {},
            "meal_suggestions": [],
            "dietary_considerations": []
        }
        
        # Determine nutrition goal based on fitness goals
        nutrition_goal = await self._determine_nutrition_goal(goals)
        nutrition_plan["goal"] = nutrition_goal
        
        # Calculate macronutrient requirements
        macros = await self._calculate_macros(nutrition_goal, fitness_plan)
        nutrition_plan.update(macros)
        
        # Design meal timing strategy
        meal_timing = await self._design_meal_timing(fitness_plan, nutrition_goal)
        nutrition_plan["meal_timing"] = meal_timing
        
        # Select supplements
        supplements = await self._select_supplements(goals, constraints)
        nutrition_plan["supplements"] = supplements
        
        # Design hydration strategy
        hydration = await self._design_hydration(fitness_plan)
        nutrition_plan["hydration"] = hydration
        
        # Generate meal suggestions
        meal_suggestions = await self._generate_meal_suggestions(nutrition_plan, preferences)
        nutrition_plan["meal_suggestions"] = meal_suggestions
        
        # Add dietary considerations
        dietary_considerations = await self._add_dietary_considerations(constraints, preferences)
        nutrition_plan["dietary_considerations"] = dietary_considerations
        
        return nutrition_plan
    
    async def _determine_nutrition_goal(self, goals: List[str]) -> str:
        """Determine primary nutrition goal based on fitness goals."""
        
        if "weight_loss" in goals:
            return "Create a moderate caloric deficit while preserving muscle mass"
        elif "muscle_gain" in goals:
            return "Create a moderate caloric surplus to support muscle growth"
        elif "strength_improvement" in goals:
            return "Maintain bodyweight while optimizing performance and recovery"
        elif "endurance" in goals:
            return "Optimize carbohydrate intake for performance and recovery"
        elif "core_restoration" in goals or "pelvic_floor_recovery" in goals:
            return "Support recovery and healing with adequate protein and nutrients"
        else:
            return "Maintain current bodyweight while supporting overall health and fitness"
    
    async def _calculate_macros(self, nutrition_goal: str, fitness_plan: Dict[str, Any]) -> Dict[str, str]:
        """Calculate macronutrient requirements."""
        
        nutrition_tool = self.get_tool("nutrition_calculator")
        
        # Default values for demo (in real implementation, get from user profile)
        weight = 70  # kg
        activity_level = "moderately_active"
        age = 30
        gender = "female"
        
        # Determine goal for calculation
        if "deficit" in nutrition_goal:
            calc_goal = "weight_loss"
        elif "surplus" in nutrition_goal:
            calc_goal = "muscle_gain"
        else:
            calc_goal = "maintenance"
        
        macros = await nutrition_tool.execute(
            goal=calc_goal,
            weight=weight,
            activity_level=activity_level,
            age=age,
            gender=gender
        )
        
        return {
            "calories": f"{macros['calories']} calories per day",
            "protein": f"{macros['protein_g']}g protein per day",
            "carbohydrate": f"{macros['carbs_g']}g carbohydrates per day",
            "fat": f"{macros['fat_g']}g fat per day"
        }
    
    async def _design_meal_timing(self, fitness_plan: Dict[str, Any], nutrition_goal: str) -> List[str]:
        """Design meal timing strategy based on fitness plan."""
        
        meal_timing = []
        
        # Pre-workout nutrition
        meal_timing.append("2-3 hours before exercise: Balanced meal with protein and carbohydrates")
        meal_timing.append("30-60 minutes before exercise: Light snack with carbohydrates if needed")
        
        # Post-workout nutrition
        meal_timing.append("Within 2 hours after exercise: Protein and carbohydrates for recovery")
        
        # General meal timing
        meal_timing.append("Eat every 3-4 hours to maintain stable energy levels")
        meal_timing.append("Include protein with each meal to support muscle maintenance")
        
        # Goal-specific timing
        if "deficit" in nutrition_goal:
            meal_timing.append("Focus on high-fiber foods to promote satiety")
        elif "surplus" in nutrition_goal:
            meal_timing.append("Consider additional meal or snack to meet caloric needs")
        
        return meal_timing
    
    async def _select_supplements(self, goals: List[str], constraints: List[str]) -> List[str]:
        """Select appropriate supplements based on goals and constraints."""
        
        supplements = []
        
        # Core supplements
        supplements.append("Multivitamin: To ensure adequate micronutrient intake")
        supplements.append("Vitamin D3: 1000-2000 IU daily (especially important for postpartum)")
        
        # Goal-specific supplements
        if "strength" in goals or "muscle_gain" in goals:
            supplements.append("Creatine monohydrate: 3-5g daily")
            supplements.append("Whey protein: To meet protein targets")
        
        if "endurance" in goals:
            supplements.append("Electrolyte supplement: For longer training sessions")
        
        # Constraint-specific supplements
        if "postpartum" in constraints:
            supplements.append("Omega-3 fatty acids: Support brain health and recovery")
            supplements.append("Iron: If recommended by healthcare provider")
        
        # Safety note
        supplements.append("Consult healthcare provider before starting any new supplements")
        
        return supplements
    
    async def _design_hydration(self, fitness_plan: Dict[str, Any]) -> Dict[str, str]:
        """Design hydration strategy."""
        
        hydration = {
            "daily_water": "2-3 liters of water per day (adjust based on activity and climate)",
            "pre_exercise": "500ml water 2-3 hours before exercise",
            "during_exercise": "150-300ml every 15-20 minutes during exercise",
            "post_exercise": "500ml water after exercise, plus electrolytes if needed",
            "signs_of_dehydration": "Monitor urine color (should be light yellow) and thirst levels"
        }
        
        return hydration
    
    async def _generate_meal_suggestions(self, nutrition_plan: Dict[str, Any], 
                                       preferences: List[str]) -> List[Dict[str, str]]:
        """Generate meal suggestions based on nutrition plan and preferences."""
        
        meal_suggestions = []
        
        # Breakfast suggestions
        breakfast_options = [
            {
                "meal": "Breakfast",
                "suggestion": "Greek yogurt with berries and nuts",
                "macros": "Protein: 20g, Carbs: 25g, Fat: 15g"
            },
            {
                "meal": "Breakfast",
                "suggestion": "Oatmeal with protein powder and banana",
                "macros": "Protein: 25g, Carbs: 45g, Fat: 8g"
            }
        ]
        
        # Lunch suggestions
        lunch_options = [
            {
                "meal": "Lunch",
                "suggestion": "Grilled chicken salad with mixed greens and olive oil",
                "macros": "Protein: 30g, Carbs: 15g, Fat: 20g"
            },
            {
                "meal": "Lunch",
                "suggestion": "Quinoa bowl with vegetables and lean protein",
                "macros": "Protein: 25g, Carbs: 40g, Fat: 12g"
            }
        ]
        
        # Dinner suggestions
        dinner_options = [
            {
                "meal": "Dinner",
                "suggestion": "Salmon with sweet potato and steamed vegetables",
                "macros": "Protein: 35g, Carbs: 30g, Fat: 18g"
            },
            {
                "meal": "Dinner",
                "suggestion": "Lean beef stir-fry with brown rice",
                "macros": "Protein: 30g, Carbs: 35g, Fat: 15g"
            }
        ]
        
        meal_suggestions.extend(breakfast_options)
        meal_suggestions.extend(lunch_options)
        meal_suggestions.extend(dinner_options)
        
        return meal_suggestions
    
    async def _add_dietary_considerations(self, constraints: List[str], 
                                        preferences: List[str]) -> List[str]:
        """Add dietary considerations based on constraints and preferences."""
        
        considerations = []
        
        # Constraint-based considerations
        if "postpartum" in constraints:
            considerations.append("Ensure adequate calcium intake for bone health")
            considerations.append("Include iron-rich foods to support recovery")
            considerations.append("Consider breastfeeding nutrition if applicable")
        
        if "diastasis_recti" in constraints:
            considerations.append("Focus on anti-inflammatory foods to support healing")
            considerations.append("Ensure adequate protein for tissue repair")
        
        # Preference-based considerations
        if "vegetarian" in preferences:
            considerations.append("Include plant-based protein sources")
            considerations.append("Consider B12 supplementation")
        
        if "gluten_free" in preferences:
            considerations.append("Choose gluten-free grains and products")
        
        # General considerations
        considerations.append("Focus on whole, minimally processed foods")
        considerations.append("Include a variety of colorful fruits and vegetables")
        considerations.append("Limit added sugars and processed foods")
        
        return considerations

