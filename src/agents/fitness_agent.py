import asyncio
from typing import List, Dict, Any
from .base_agent import BaseAgent
from ..tools.planning_tools import ExerciseDatabaseTool, ProgressionModelTool
from ..utils.config import Config
import openai

class FitnessAgent(BaseAgent):
    """Agent responsible for designing fitness components of health plans."""
    
    def __init__(self):
        super().__init__(
            name="Fitness Agent",
            description="Designs workout plans, stretching routines, and mobility work"
        )
        
        # Add fitness tools
        self.add_tool(ExerciseDatabaseTool())
        self.add_tool(ProgressionModelTool())
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def process(self, research_findings: Dict[str, Any], goals: List[str], 
                     constraints: List[str], timeline: str, fitness_level: str) -> Dict[str, Any]:
        """Design fitness component based on research and requirements."""
        
        # Get the comprehensive 7-day organized structure
        organized_days = await self._organize_by_days(goals, constraints, fitness_level)
        
        # Create global rules
        global_rules = await self._create_global_rules(research_findings, constraints)
        
        # Add safety considerations
        safety_considerations = await self._add_safety_considerations(research_findings, constraints)
        
        # Return the organized structure directly
        fitness_plan = organized_days
        fitness_plan["global_rules"] = global_rules
        fitness_plan["safety_considerations"] = safety_considerations
        
        return fitness_plan
    
    async def _design_weekly_split(self, goals: List[str], timeline: str, fitness_level: str) -> List[str]:
        """Design weekly training split."""
        
        # Define splits based on goals and fitness level
        splits = {
            "postpartum_reconditioning": [
                "Week 1-4: Foundation Phase",
                "Week 5-8: Progressive Phase",
                "Week 9-12: Integration Phase"
            ],
            "weight_loss": [
                "Mon: Upper A",
                "Tue: Lower A", 
                "Wed: Conditioning",
                "Thu: Upper B",
                "Fri: Lower B",
                "Sat: Active Recovery",
                "Sun: Rest"
            ],
            "strength_training": [
                "Mon: Squat + Bench",
                "Tue: Deadlift + Press",
                "Wed: Rest",
                "Thu: Squat + Bench",
                "Fri: Deadlift + Accessories",
                "Sat: Rest",
                "Sun: Rest"
            ]
        }
        
        # Determine primary goal for split selection
        primary_goal = goals[0] if goals else "general_fitness"
        
        if "postpartum" in primary_goal:
            return splits["postpartum_reconditioning"]
        elif "weight_loss" in primary_goal:
            return splits["weight_loss"]
        elif "strength" in primary_goal:
            return splits["strength_training"]
        else:
            return [
                "Mon: Full Body A",
                "Tue: Rest",
                "Wed: Full Body B", 
                "Thu: Rest",
                "Fri: Full Body C",
                "Sat: Active Recovery",
                "Sun: Rest"
            ]
    
    async def _select_exercises(self, goals: List[str], constraints: List[str], 
                              fitness_level: str) -> Dict[str, List[Dict[str, Any]]]:
        """Select appropriate exercises for the plan."""
        
        exercise_tool = self.get_tool("exercise_database")
        exercises = {}
        
        # Define exercise categories based on goals
        categories = []
        if "core_restoration" in goals:
            categories.extend(["core", "pelvic_floor"])
        if "strength" in goals:
            categories.extend(["strength", "compound"])
        if "endurance" in goals:
            categories.extend(["cardio", "endurance"])
        if "flexibility" in goals:
            categories.extend(["mobility", "stretching"])
        
        # If no specific categories, use general fitness
        if not categories:
            categories = ["strength", "core", "cardio"]
        
        # Select exercises for each category
        for category in categories:
            category_exercises = await exercise_tool.execute(
                category=category,
                difficulty=fitness_level,
                equipment=[]
            )
            
            if category_exercises:
                exercises[category] = category_exercises
        
        # Organize exercises by training days
        organized_exercises = await self._organize_by_days(exercises, goals)
        
        return organized_exercises
    
    async def _organize_by_days(self, goals: List[str], constraints: List[str], 
                               fitness_level: str) -> Dict[str, List[Dict[str, Any]]]:
        """Organize exercises into comprehensive training days with 30-60 minute workouts."""
        
        organized = {}
        
        # Create comprehensive 7-day workout plan
        if "senior_fitness" in goals or "mobility" in goals or "balance" in goals:
            # Senior fitness focused plan
            organized["Full Body A"] = [
                {"name": "Gentle warm-up walk", "sets": "1", "reps": "5-10 min", "rest": "N/A", "notes": "Start slow, gradually increase pace"},
                {"name": "Bodyweight squats", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Focus on form, go as deep as comfortable"},
                {"name": "Wall push-ups", "sets": "3", "reps": "8-15", "rest": "90s", "notes": "Adjust distance from wall for difficulty"},
                {"name": "Seated rows with resistance band", "sets": "3", "reps": "10-15", "rest": "90s", "notes": "Keep back straight, pull elbows back"},
                {"name": "Heel raises", "sets": "3", "reps": "12-15", "rest": "60s", "notes": "Hold onto support if needed for balance"},
                {"name": "Gentle stretching", "sets": "1", "reps": "5-10 min", "rest": "N/A", "notes": "Focus on major muscle groups"}
            ]
            
            organized["Mobility & Balance"] = [
                {"name": "Tai Chi warm-up", "sets": "1", "reps": "10-15 min", "rest": "N/A", "notes": "Slow, controlled movements"},
                {"name": "Single-leg balance", "sets": "3", "reps": "30s each leg", "rest": "60s", "notes": "Hold onto support initially"},
                {"name": "Hip circles", "sets": "2", "reps": "10 each direction", "rest": "30s", "notes": "Gentle circular movements"},
                {"name": "Shoulder rolls", "sets": "2", "reps": "10 forward, 10 backward", "rest": "30s", "notes": "Full range of motion"},
                {"name": "Ankle mobility", "sets": "2", "reps": "10 each foot", "rest": "30s", "notes": "Point and flex toes"},
                {"name": "Cool-down walk", "sets": "1", "reps": "5-10 min", "rest": "N/A", "notes": "Gradual slowdown"}
            ]
            
            organized["Full Body B"] = [
                {"name": "Light cardio warm-up", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Walking, cycling, or swimming"},
                {"name": "Step-ups", "sets": "3", "reps": "8-12 each leg", "rest": "90s", "notes": "Use low step, focus on control"},
                {"name": "Modified plank", "sets": "3", "reps": "20-40s", "rest": "90s", "notes": "Knees down if needed"},
                {"name": "Seated shoulder press", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Light weights, full range of motion"},
                {"name": "Seated leg extensions", "sets": "3", "reps": "10-15", "rest": "90s", "notes": "Slow and controlled"},
                {"name": "Gentle yoga flow", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Sun salutation variations"}
            ]
            
            organized["Active Recovery"] = [
                {"name": "Gentle walking", "sets": "1", "reps": "20-30 min", "rest": "N/A", "notes": "Conversational pace"},
                {"name": "Light stretching", "sets": "1", "reps": "10-15 min", "rest": "N/A", "notes": "Hold each stretch 20-30s"},
                {"name": "Deep breathing", "sets": "1", "reps": "5 min", "rest": "N/A", "notes": "4-7-8 breathing pattern"},
                {"name": "Foam rolling", "sets": "1", "reps": "10 min", "rest": "N/A", "notes": "Gentle pressure on major muscles"}
            ]
            
            organized["Full Body C"] = [
                {"name": "Dynamic warm-up", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Arm circles, hip swings, ankle rolls"},
                {"name": "Chair squats", "sets": "3", "reps": "10-15", "rest": "90s", "notes": "Sit and stand, use chair for safety"},
                {"name": "Standing rows", "sets": "3", "reps": "10-15", "rest": "90s", "notes": "Resistance band or light weights"},
                {"name": "Side leg raises", "sets": "3", "reps": "8-12 each leg", "rest": "90s", "notes": "Hold onto support for balance"},
                {"name": "Chest stretch", "sets": "3", "reps": "30s hold", "rest": "60s", "notes": "Doorway stretch or corner stretch"},
                {"name": "Cool-down stretches", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Focus on tight areas"}
            ]
            
            organized["Rest Day"] = [
                {"name": "Light walking", "sets": "1", "reps": "15-20 min", "rest": "N/A", "notes": "Optional, very light pace"},
                {"name": "Gentle stretching", "sets": "1", "reps": "10 min", "rest": "N/A", "notes": "Only if feeling good"},
                {"name": "Restorative activities", "sets": "1", "reps": "As desired", "rest": "N/A", "notes": "Reading, meditation, light hobbies"}
            ]
            
        elif "postpartum" in goals or "core_restoration" in goals:
            # Postpartum specific plan
            organized["Foundation Phase"] = [
                {"name": "Pelvic floor activation", "sets": "3", "reps": "5-10", "rest": "60s", "notes": "Kegels, gentle contractions"},
                {"name": "Gentle walking", "sets": "1", "reps": "15-20 min", "rest": "N/A", "notes": "Flat surface, comfortable pace"},
                {"name": "Pelvic tilts", "sets": "3", "reps": "10-15", "rest": "60s", "notes": "Lie on back, gentle movements"},
                {"name": "Deep breathing", "sets": "1", "reps": "5 min", "rest": "N/A", "notes": "Diaphragmatic breathing"},
                {"name": "Gentle stretching", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Focus on major muscle groups"}
            ]
            
            organized["Progressive Phase"] = [
                {"name": "Pelvic floor exercises", "sets": "3", "reps": "10", "rest": "60s", "notes": "Progressive intensity"},
                {"name": "Bird dog", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Start on hands and knees"},
                {"name": "Modified plank", "sets": "3", "reps": "20-30s", "rest": "90s", "notes": "Knees down, build endurance"},
                {"name": "Gentle squats", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Use support if needed"},
                {"name": "Walking intervals", "sets": "3", "reps": "5 min", "rest": "2 min", "notes": "Gradually increase pace"}
            ]
            
            organized["Integration Phase"] = [
                {"name": "Dead bug", "sets": "3", "reps": "10-15", "rest": "90s", "notes": "Core stability focus"},
                {"name": "Bodyweight squats", "sets": "3", "reps": "10-15", "rest": "90s", "notes": "Full range of motion"},
                {"name": "Modified push-ups", "sets": "3", "reps": "5-10", "rest": "90s", "notes": "Knees down or wall push-ups"},
                {"name": "Walking lunges", "sets": "2", "reps": "8-10 each leg", "rest": "90s", "notes": "Light and controlled"},
                {"name": "Core stabilization", "sets": "3", "reps": "30s hold", "rest": "60s", "notes": "Plank variations"}
            ]
            
        else:
            # General fitness plan - comprehensive 7-day structure
            organized["Full Body A"] = [
                {"name": "Dynamic warm-up", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Jumping jacks, arm circles, hip swings"},
                {"name": "Squats", "sets": "4", "reps": "8-12", "rest": "120s", "notes": "Focus on form, progressive overload"},
                {"name": "Push-ups", "sets": "3", "reps": "8-15", "rest": "90s", "notes": "Modify difficulty as needed"},
                {"name": "Rows", "sets": "3", "reps": "10-12", "rest": "90s", "notes": "Dumbbell or resistance band"},
                {"name": "Plank", "sets": "3", "reps": "30-60s", "rest": "60s", "notes": "Build core endurance"},
                {"name": "Cool-down stretches", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Major muscle groups"}
            ]
            
            organized["Cardio & Mobility"] = [
                {"name": "Light cardio", "sets": "1", "reps": "20-25 min", "rest": "N/A", "notes": "Walking, cycling, or swimming"},
                {"name": "Dynamic stretching", "sets": "1", "reps": "10-15 min", "rest": "N/A", "notes": "Hip swings, leg swings, arm circles"},
                {"name": "Mobility work", "sets": "1", "reps": "10-15 min", "rest": "N/A", "notes": "Shoulder, hip, and ankle mobility"}
            ]
            
            organized["Full Body B"] = [
                {"name": "Warm-up", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Light cardio and dynamic stretches"},
                {"name": "Lunges", "sets": "3", "reps": "10-12 each leg", "rest": "90s", "notes": "Forward, reverse, and walking variations"},
                {"name": "Dips", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Chair dips or parallel bars"},
                {"name": "Pull-ups/Assisted", "sets": "3", "reps": "5-10", "rest": "120s", "notes": "Use assistance if needed"},
                {"name": "Russian twists", "sets": "3", "reps": "20-30", "rest": "60s", "notes": "Core rotation work"},
                {"name": "Cool-down", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Static stretching"}
            ]
            
            organized["Active Recovery"] = [
                {"name": "Light walking", "sets": "1", "reps": "25-30 min", "rest": "N/A", "notes": "Conversational pace"},
                {"name": "Gentle stretching", "sets": "1", "reps": "15-20 min", "rest": "N/A", "notes": "Hold stretches 30-60s"},
                {"name": "Foam rolling", "sets": "1", "reps": "10-15 min", "rest": "N/A", "notes": "Major muscle groups"}
            ]
            
            organized["Full Body C"] = [
                {"name": "Warm-up", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Dynamic movements and light cardio"},
                {"name": "Deadlift variation", "sets": "3", "reps": "8-12", "rest": "120s", "notes": "Romanian or single-leg"},
                {"name": "Overhead press", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Dumbbell or barbell"},
                {"name": "Lat pulldowns", "sets": "3", "reps": "10-12", "rest": "90s", "notes": "Focus on lat engagement"},
                {"name": "Core circuit", "sets": "3", "reps": "30s each", "rest": "60s", "notes": "Plank, side plank, dead bug"},
                {"name": "Cool-down", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Static stretching"}
            ]
            
            organized["Rest Day"] = [
                {"name": "Light activity", "sets": "1", "reps": "15-20 min", "rest": "N/A", "notes": "Optional light walking or stretching"},
                {"name": "Recovery focus", "sets": "1", "reps": "As needed", "rest": "N/A", "notes": "Sleep, hydration, nutrition"}
            ]
        
        return organized
    
    async def _design_progression(self, goals: List[str], timeline: str, 
                                fitness_level: str) -> Dict[str, Any]:
        """Design progression model."""
        
        progression_tool = self.get_tool("progression_model")
        
        primary_goal = goals[0] if goals else "general_fitness"
        
        progression = await progression_tool.execute(
            goal=primary_goal,
            timeline=timeline,
            starting_level=fitness_level
        )
        
        return progression
    
    async def _create_global_rules(self, research_findings: Dict[str, Any], 
                                 constraints: List[str]) -> List[Dict[str, str]]:
        """Create global training rules."""
        
        rules = []
        
        # Add evidence-based rules from research
        if research_findings.get("recommendations"):
            for rec in research_findings["recommendations"]:
                rules.append({
                    "title": "Research-Based Recommendation",
                    "text": rec
                })
        
        # Add constraint-specific rules
        if "diastasis_recti" in constraints:
            rules.append({
                "title": "Core Safety",
                "text": "Stop any exercise that causes doming or bulging in the abdominal area"
            })
        
        if "pelvic_organ_prolapse" in constraints:
            rules.append({
                "title": "Pelvic Floor Protection",
                "text": "Avoid exercises that increase intra-abdominal pressure"
            })
        
        # Add general safety rules
        rules.extend([
            {
                "title": "General Safety",
                "text": "Stop if you experience pain, dizziness, or unusual symptoms"
            },
            {
                "title": "Progression",
                "text": "Only progress when current level feels comfortable and manageable"
            }
        ])
        
        return rules
    
    async def _add_safety_considerations(self, research_findings: Dict[str, Any], 
                                       constraints: List[str]) -> List[str]:
        """Add safety considerations to the plan."""
        
        safety_considerations = []
        
        # Add contraindications from research
        if research_findings.get("contraindications"):
            safety_considerations.extend(research_findings["contraindications"])
        
        # Add constraint-specific considerations
        if "diastasis_recti" in constraints:
            safety_considerations.append("Monitor abdominal separation weekly")
        
        if "pelvic_organ_prolapse" in constraints:
            safety_considerations.append("Consider working with pelvic floor physical therapist")
        
        return safety_considerations

