import asyncio
import json
from typing import List, Dict, Any
from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .fitness_agent import FitnessAgent
from .nutrition_agent import NutritionAgent
from .motivation_agent import MotivationAgent
from .safety_agent import SafetyAgent
from ..utils.config import Config
from ..utils.models import HealthPlanRequest, HealthPlan
import openai

class OrchestratorAgent(BaseAgent):
    """Master coordinator that manages the entire health plan generation process."""
    
    def __init__(self):
        super().__init__(
            name="Orchestrator Agent",
            description="Coordinates all specialized agents to generate comprehensive health plans"
        )
        
        # Initialize all specialized agents
        self.research_agent = ResearchAgent()
        self.fitness_agent = FitnessAgent()
        self.nutrition_agent = NutritionAgent()
        self.motivation_agent = MotivationAgent()
        self.safety_agent = SafetyAgent()
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def process(self, **kwargs) -> Dict[str, Any]:
        """Process the agent's main task."""
        # This is the main entry point for the orchestrator
        if 'request' in kwargs:
            return await self.generate_health_plan(kwargs['request'])
        else:
            raise ValueError("Orchestrator requires a 'request' parameter")
    
    async def generate_health_plan(self, request: HealthPlanRequest) -> Dict[str, Any]:
        """Generate a comprehensive health plan using all agents."""
        
        print(f"🎯 Starting health plan generation for {request.population}")
        print(f"📋 Goals: {request.goals}")
        print(f"⚠️  Constraints: {request.constraints}")
        
        # Phase 1: Research
        print("\n🔬 Phase 1: Research")
        research_findings = await self.research_agent.process(
            population=request.population,
            goals=[goal.value for goal in request.goals],
            constraints=request.constraints
        )
        print("✅ Research phase completed")
        
        # Phase 2: Fitness Planning
        print("\n💪 Phase 2: Fitness Planning")
        fitness_plan = await self.fitness_agent.process(
            research_findings=research_findings,
            goals=[goal.value for goal in request.goals],
            constraints=request.constraints,
            timeline=request.timeline,
            fitness_level=request.fitness_level
        )
        print("✅ Fitness planning completed")
        
        # Phase 3: Nutrition Planning
        print("\n🥗 Phase 3: Nutrition Planning")
        nutrition_plan = await self.nutrition_agent.process(
            fitness_plan=fitness_plan,
            goals=[goal.value for goal in request.goals],
            constraints=request.constraints,
            preferences=request.preferences
        )
        print("✅ Nutrition planning completed")
        
        # Phase 4: Motivation Planning
        print("\n🎯 Phase 4: Motivation Planning")
        motivation_plan = await self.motivation_agent.process(
            goals=[goal.value for goal in request.goals],
            timeline=request.timeline,
            fitness_level=request.fitness_level,
            constraints=request.constraints
        )
        print("✅ Motivation planning completed")
        
        # Phase 5: Safety Validation
        print("\n🛡️ Phase 5: Safety Validation")
        safety_report = await self.safety_agent.process(
            fitness_plan=fitness_plan,
            nutrition_plan=nutrition_plan,
            motivation_plan=motivation_plan,
            constraints=request.constraints,
            research_findings=research_findings
        )
        print("✅ Safety validation completed")
        
        # Phase 6: Plan Integration and Formatting
        print("\n🔧 Phase 6: Plan Integration")
        final_plan = await self._integrate_plan(
            request=request,
            research_findings=research_findings,
            fitness_plan=fitness_plan,
            nutrition_plan=nutrition_plan,
            motivation_plan=motivation_plan,
            safety_report=safety_report
        )
        print("✅ Plan integration completed")
        
        print(f"\n🎉 Health plan generation completed!")
        print(f"📊 Safety Rating: {safety_report['overall_safety']}")
        print(f"📈 Validation Score: {safety_report['validation_score']}/100")
        
        return final_plan
    
    async def _integrate_plan(self, request: HealthPlanRequest, research_findings: Dict[str, Any],
                            fitness_plan: Dict[str, Any], nutrition_plan: Dict[str, Any],
                            motivation_plan: Dict[str, Any], safety_report: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate all components into a final health plan."""
        
        # Create overview
        overview = await self._generate_overview(request, research_findings)
        
        # Create execution checklist
        execution_checklist = await self._create_execution_checklist(
            fitness_plan, nutrition_plan, motivation_plan, safety_report
        )
        
        # Format the final plan
        final_plan = {
            request.population: {
                "overview": overview,
                "research_basis": {
                    "evidence_level": "A",
                    "sources": ["Research synthesis", "Healthcare guidelines"],
                    "last_updated": "2024",
                    "findings": research_findings
                },
                "fitness_component": fitness_plan,
                "nutrition_component": nutrition_plan,
                "motivation_component": motivation_plan,
                "safety_protocols": safety_report,
                "execution_checklist": execution_checklist
            }
        }
        
        return final_plan
    
    async def _generate_overview(self, request: HealthPlanRequest, 
                               research_findings: Dict[str, Any]) -> str:
        """Generate plan overview."""
        
        overview_prompt = f"""
        Create a comprehensive overview for a {request.population} health plan.
        
        Goals: {[goal.value for goal in request.goals]}
        Timeline: {request.timeline}
        Fitness Level: {request.fitness_level}
        Constraints: {request.constraints}
        
        The overview should:
        1. Explain the purpose and approach of the plan
        2. Highlight key components (fitness, nutrition, motivation)
        3. Emphasize safety and evidence-based approach
        4. Set expectations for results and timeline
        5. Be encouraging and motivating
        
        Keep it concise but comprehensive (2-3 paragraphs).
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": overview_prompt}],
                max_tokens=500,
                temperature=Config.TEMPERATURE
            )
            
            return response.choices[0].message.content
        except Exception as e:
            # Fallback overview
            return f"""
            This comprehensive {request.population} health plan is designed to help you achieve your goals of {[goal.value for goal in request.goals]} over {request.timeline}.
            
            The plan integrates evidence-based fitness programming, personalized nutrition guidance, and motivational strategies to support your journey. It's specifically tailored for {request.fitness_level} fitness level and takes into account your unique constraints and preferences.
            
            Safety is our top priority, with built-in validation and modification protocols to ensure your well-being throughout the program. Follow the plan consistently, listen to your body, and celebrate your progress along the way.
            """
    
    async def _create_execution_checklist(self, fitness_plan: Dict[str, Any], 
                                        nutrition_plan: Dict[str, Any],
                                        motivation_plan: Dict[str, Any],
                                        safety_report: Dict[str, Any]) -> List[str]:
        """Create execution checklist for the plan."""
        
        checklist = []
        
        # Pre-start checklist
        checklist.extend([
            "Obtain medical clearance if required",
            "Set up tracking systems for progress monitoring",
            "Prepare workout space and equipment",
            "Plan meals and grocery shopping",
            "Set up accountability systems"
        ])
        
        # Weekly checklist
        checklist.extend([
            "Review and adjust plan based on progress",
            "Track key metrics and measurements",
            "Ensure adequate rest and recovery",
            "Stay hydrated and follow nutrition guidelines",
            "Celebrate small wins and progress"
        ])
        
        # Safety checklist
        if safety_report["overall_safety"] != "low_risk":
            checklist.extend([
                "Monitor for any concerning symptoms",
                "Have emergency contact information readily available",
                "Consider working with a qualified professional"
            ])
        
        # Goal-specific checklist
        if "core_restoration" in str(fitness_plan):
            checklist.extend([
                "Monitor abdominal separation weekly",
                "Focus on proper breathing techniques",
                "Avoid exercises that cause doming"
            ])
        
        return checklist

    async def _create_days_structure(self, fitness_plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """Create days structure in frontend-compatible format."""
        days = {}
        
        # Check for exercises in the fitness plan
        if "exercises" in fitness_plan:
            for day, exercises in fitness_plan["exercises"].items():
                formatted_exercises = []
                for i, exercise in enumerate(exercises, 1):
                    if isinstance(exercise, dict):
                        # Convert exercise dict to string format
                        name = exercise.get("name", "Exercise")
                        sets = exercise.get("sets", 3)
                        reps = exercise.get("reps", "8-12")
                        notes = exercise.get("notes", "")
                        
                        # Format: "1) Exercise Name — Sets×Reps"
                        exercise_text = f"{i}) {name} — {sets}×{reps}"
                        if notes:
                            exercise_text += f" ({notes})"
                        formatted_exercises.append(exercise_text)
                    else:
                        formatted_exercises.append(f"{i}) {exercise}")
                days[day] = formatted_exercises
        
        # Also check for exercise_program (backward compatibility)
        elif "exercise_program" in fitness_plan:
            for day, exercises in fitness_plan["exercise_program"].items():
                formatted_exercises = []
                for i, exercise in enumerate(exercises, 1):
                    if isinstance(exercise, dict):
                        # Convert exercise dict to string format
                        name = exercise.get("name", "Exercise")
                        sets = exercise.get("sets", 3)
                        reps = exercise.get("reps", "8-12")
                        formatted_exercises.append(f"{i}) {name} — {sets}×{reps}")
                    else:
                        formatted_exercises.append(f"{i}) {exercise}")
                days[day] = formatted_exercises
        
        # Default structure if none exists
        if not days:
            days = {
                "Full Body A": [
                    "1) Bodyweight squats — 3×10-15",
                    "2) Push-ups — 3×5-10",
                    "3) Walking lunges — 2×10/leg",
                    "4) Plank — 3×30 seconds"
                ]
            }
        
        return days
