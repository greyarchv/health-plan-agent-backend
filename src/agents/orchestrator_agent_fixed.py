import asyncio
from typing import List, Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.config import Config
import openai

class OrchestratorAgentFixed(BaseAgent):
    """Fixed orchestrator agent that generates comprehensive, frontend-compatible health plans."""
    
    def __init__(self):
        super().__init__(
            name="Orchestrator Agent",
            description="Coordinates all agents to create comprehensive health plans"
        )
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Initialize specialized agents
        from src.agents.research_agent import ResearchAgent
        from src.agents.fitness_agent import FitnessAgent
        from src.agents.nutrition_agent import NutritionAgent
        from src.agents.motivation_agent import MotivationAgent
        from src.agents.safety_agent import SafetyAgent
        
        self.research_agent = ResearchAgent()
        self.fitness_agent = FitnessAgent()
        self.nutrition_agent = NutritionAgent()
        self.motivation_agent = MotivationAgent()
        self.safety_agent = SafetyAgent()
    
    async def process(self, request) -> Dict[str, Any]:
        """Process health plan request."""
        return await self.generate_health_plan(request)
    
    async def generate_health_plan(self, request) -> Dict[str, Any]:
        """Generate a comprehensive health plan using all agents."""
        
        # Check if this is a simple prompt request
        if hasattr(request, 'prompt') and request.prompt:
            print(f"🎯 Simple prompt received: {request.prompt}")
            print("🧠 Using LLM to enhance prompt and extract parameters...")
            
            # Use LLM to enhance the simple prompt
            enhanced_prompt = await self._enhance_user_prompt(request.prompt)
            print(f"✨ Enhanced prompt: {enhanced_prompt}")
            
            # Extract parameters from the enhanced prompt
            extracted_params = await self._extract_parameters_from_prompt(enhanced_prompt)
            print(f"📋 Extracted parameters: {extracted_params}")
            
            # Use extracted parameters for the rest of the process
            population = extracted_params.get('population', 'general')
            goals = extracted_params.get('goals', ['general_fitness'])
            constraints = extracted_params.get('constraints', [])
            timeline = extracted_params.get('timeline', '12_weeks')
            fitness_level = extracted_params.get('fitness_level', 'beginner')
            preferences = extracted_params.get('preferences', [])
        else:
            # Use the structured request as before
            population = request.population
            goals = request.goals
            constraints = request.constraints
            timeline = request.timeline
            fitness_level = request.fitness_level
            preferences = request.preferences
        
        print(f"🎯 Starting health plan generation for {population}")
        print(f"📋 Goals: {goals}")
        print(f"⚠️  Constraints: {constraints}")
        print(f"⏱️ Timeline: {timeline}")
        print(f"💪 Fitness Level: {fitness_level}")
        
        # Phase 1: Research
        print("\n🔬 Phase 1: Research")
        research_findings = await self.research_agent.process(
            population=population,
            goals=list(goals),
            constraints=constraints
        )
        print("✅ Research phase completed")
        
        # Phase 2: Fitness Planning
        print("\n💪 Phase 2: Fitness Planning")
        print(f"💪 Calling fitness agent with goals: {goals}")
        fitness_plan = await self.fitness_agent.process(
            research_findings=research_findings,
            goals=list(goals),
            constraints=constraints,
            timeline=timeline,
            fitness_level=fitness_level
        )
        print(f"💪 Fitness plan keys: {list(fitness_plan.keys())}")
        print("✅ Fitness planning completed")
        
        # Phase 3: Nutrition Planning
        print("\n🥗 Phase 3: Nutrition Planning")
        nutrition_plan = await self.nutrition_agent.process(
            fitness_plan=fitness_plan,
            goals=list(goals),
            constraints=constraints,
            preferences=preferences
        )
        print("✅ Nutrition planning completed")
        
        # Phase 4: Motivation Planning
        print("\n🎯 Phase 4: Motivation Planning")
        motivation_plan = await self.motivation_agent.process(
            goals=list(goals),
            timeline=timeline,
            fitness_level=fitness_level,
            constraints=constraints
        )
        print("✅ Motivation planning completed")
        
        # Phase 5: Safety Validation
        print("\n🛡️ Phase 5: Safety Validation")
        safety_report = await self.safety_agent.process(
            fitness_plan=fitness_plan,
            nutrition_plan=nutrition_plan,
            motivation_plan=motivation_plan,
            constraints=constraints,
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
        print(f"📊 Safety Rating: {safety_report.get('overall_safety', 'unknown')}")
        print(f"📈 Validation Score: {safety_report.get('validation_score', 0)}/100")
        
        return final_plan
    
    async def _enhance_user_prompt(self, user_prompt: str) -> str:
        """Use LLM to enhance a simple user prompt into a comprehensive health plan request."""
        try:
            enhancement_prompt = f"""
You are an expert health and fitness consultant. A user has provided a simple request for a health plan:

USER REQUEST: "{user_prompt}"

Your task is to enhance this into a comprehensive, detailed health plan specification that covers:

1. POPULATION: Who this plan is for (e.g., postpartum_mothers, senior_fitness, athletes, etc.)
2. GOALS: Specific fitness and health objectives
3. CONSTRAINTS: Any limitations, injuries, or considerations
4. TIMELINE: How long the plan should run (e.g., 8_weeks, 12_weeks, 16_weeks)
5. FITNESS_LEVEL: Beginner, intermediate, or advanced
6. PREFERENCES: Any specific preferences or requirements

Make the enhanced prompt comprehensive, specific, and actionable. Focus on what would make this the BEST possible plan for the user's needs.

ENHANCED PROMPT:
"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": enhancement_prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            print(f"🧠 LLM enhanced prompt: {enhanced_prompt}")
            return enhanced_prompt
            
        except Exception as e:
            print(f"❌ Error enhancing prompt: {e}")
            # Fallback to a basic enhancement
            return f"Create a comprehensive health plan for: {user_prompt}. Focus on evidence-based approaches, safety, and results."
    
    async def _extract_parameters_from_prompt(self, enhanced_prompt: str) -> Dict[str, Any]:
        """Use LLM to extract structured parameters from the enhanced prompt."""
        try:
            extraction_prompt = f"""
You are an expert at analyzing health plan requests and extracting key parameters.

ENHANCED PROMPT: "{enhanced_prompt}"

Extract the following parameters and return them as a JSON object:

{{
    "population": "specific population group (e.g., postpartum_mothers, senior_fitness, athletes)",
    "goals": ["goal1", "goal2", "goal3"],
    "constraints": ["constraint1", "constraint2"],
    "timeline": "8_weeks, 12_weeks, or 16_weeks",
    "fitness_level": "beginner, intermediate, or advanced",
    "preferences": ["preference1", "preference2"]
}}

If any parameter is not clearly specified, make a reasonable assumption based on the context.
Return ONLY the JSON object, no other text.
"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from the response
            try:
                import json
                # Remove any markdown formatting
                if extracted_text.startswith('```json'):
                    extracted_text = extracted_text[7:-3]
                elif extracted_text.startswith('```'):
                    extracted_text = extracted_text[3:-3]
                
                extracted_params = json.loads(extracted_text)
                print(f"📋 Extracted parameters: {extracted_params}")
                return extracted_params
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"❌ Raw response: {extracted_text}")
                # Fallback to default parameters
                return {
                    "population": "general",
                    "goals": ["general_fitness"],
                    "constraints": [],
                    "timeline": "12_weeks",
                    "fitness_level": "beginner",
                    "preferences": []
                }
                
        except Exception as e:
            print(f"❌ Error extracting parameters: {e}")
            # Fallback to default parameters
            return {
                "population": "general",
                "goals": ["general_fitness"],
                "constraints": [],
                "timeline": "12_weeks",
                "fitness_level": "beginner",
                "preferences": []
            }
    
    async def _integrate_plan(self, request, research_findings: Dict[str, Any],
                            fitness_plan: Dict[str, Any], nutrition_plan: Dict[str, Any],
                            motivation_plan: Dict[str, Any], safety_report: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate all components into a final health plan in frontend-compatible format."""
        
        # Create overview
        overview = await self._generate_overview(request, research_findings)
        
        # Create weekly split based on fitness plan
        weekly_split = await self._create_weekly_split(fitness_plan)
        
        # Create global rules from safety and fitness components
        global_rules = await self._create_global_rules(fitness_plan, safety_report)
        
        # Create days structure from fitness plan
        days = await self._create_days_structure(fitness_plan)
        
        # Create conditioning and recovery
        conditioning_and_recovery = await self._create_conditioning_recovery(fitness_plan, safety_report)
        
        # Create nutrition section
        nutrition = await self._create_nutrition_section(nutrition_plan)
        
        # Create execution checklist
        execution_checklist = await self._create_execution_checklist(
            fitness_plan, nutrition_plan, motivation_plan, safety_report
        )
        
        # Generate plan ID from population and goals
        plan_id = await self._generate_plan_id(request)
        
        # Format the final plan in exact frontend-compatible structure
        final_plan = {
            plan_id: {
                "overview": overview,
                "weekly_split": weekly_split,
                "global_rules": global_rules,
                "days": days,
                "conditioning_and_recovery": conditioning_and_recovery,
                "nutrition": nutrition,
                "execution_checklist": execution_checklist
            }
        }
        
        return final_plan
    
    async def _generate_plan_id(self, request) -> str:
        """Generate a unique plan ID from population and goals."""
        population_slug = request.population.lower().replace(" ", "_").replace("-", "_")
        goals_slug = "_".join([goal.lower().replace(" ", "_") for goal in request.goals[:2]])
        return f"{population_slug}_{goals_slug}"
    
    async def _create_weekly_split(self, fitness_plan: Dict[str, Any]) -> List[str]:
        """Create weekly split in frontend-compatible format."""
        if "weekly_split" in fitness_plan:
            return fitness_plan["weekly_split"]
        
        # Default weekly split
        return [
            "Mon: Full Body A",
            "Tue: Rest",
            "Wed: Full Body B", 
            "Thu: Rest",
            "Fri: Full Body C",
            "Sat: Active Recovery",
            "Sun: Rest"
        ]
    
    async def _create_global_rules(self, fitness_plan: Dict[str, Any], safety_report: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create global rules in frontend-compatible format."""
        rules = []
        
        # Add safety rules
        if "safety_guidelines" in safety_report:
            for guideline in safety_report["safety_guidelines"]:
                rules.append({
                    "title": "Safety",
                    "text": guideline
                })
        
        # Add fitness rules
        if "training_principles" in fitness_plan:
            for principle in fitness_plan["training_principles"]:
                rules.append({
                    "title": "Training",
                    "text": principle
                })
        
        # Add default rules if none exist
        if not rules:
            rules = [
                {
                    "title": "Progression",
                    "text": "Start with lighter weights and gradually increase as you become comfortable with the movements."
                },
                {
                    "title": "Form",
                    "text": "Focus on proper form and technique before increasing intensity or weight."
                }
            ]
        
        return rules
    
    async def _create_days_structure(self, fitness_plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """Create days structure in frontend-compatible format."""
        days = {}
        
        # Debug: Print what we're receiving
        print(f"DEBUG: Fitness plan keys: {list(fitness_plan.keys())}")
        
        # Check if we have AI-generated plan with 'days' structure
        if "days" in fitness_plan:
            # This is the new AI-generated structure
            for day, exercises in fitness_plan["days"].items():
                if isinstance(exercises, list) and exercises:
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
        # Check if we have the old organized structure (backward compatibility)
        elif "Full Body A" in fitness_plan or "Foundation Phase" in fitness_plan or "Mobility & Balance" in fitness_plan:
            # This is the old organized structure from fitness agent
            for day, exercises in fitness_plan.items():
                if isinstance(exercises, list) and exercises:
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
        
        # If no organized days found, check for nested structures
        elif "exercises" in fitness_plan:
            exercises_data = fitness_plan["exercises"]
            if isinstance(exercises_data, dict):
                for day, exercises in exercises_data.items():
                    formatted_exercises = []
                    for i, exercise in enumerate(exercises, 1):
                        if isinstance(exercise, dict):
                            name = exercise.get("name", "Exercise")
                            sets = exercise.get("sets", 3)
                            reps = exercise.get("reps", "8-12")
                            notes = exercise.get("notes", "")
                            
                            exercise_text = f"{i}) {name} — {sets}×{reps}"
                            if notes:
                                exercise_text += f" ({notes})"
                            formatted_exercises.append(exercise_text)
                        else:
                            formatted_exercises.append(f"{i}) {exercise}")
                    days[day] = formatted_exercises
        
        # If still no days found, create default structure
        if not days:
            print("DEBUG: No days found, creating default structure")
            days = {
                "Full Body A": [
                    "1) Bodyweight squats — 3×10-15",
                    "2) Push-ups — 3×5-10", 
                    "3) Walking lunges — 2×10/leg",
                    "4) Plank — 3×30 seconds"
                ]
            }
        
        print(f"DEBUG: Final days structure: {list(days.keys())}")
        return days
    
    async def _create_conditioning_recovery(self, fitness_plan: Dict[str, Any], safety_report: Dict[str, Any]) -> List[str]:
        """Create conditioning and recovery section."""
        recovery_items = []
        
        if "recovery_protocols" in fitness_plan:
            recovery_items.extend(fitness_plan["recovery_protocols"])
        
        if "conditioning_guidelines" in fitness_plan:
            recovery_items.extend(fitness_plan["conditioning_guidelines"])
        
        # Default recovery items
        if not recovery_items:
            recovery_items = [
                "Include 10-15 minutes of daily mobility work",
                "Prioritize sleep and stress management",
                "Listen to your body and rest when needed"
            ]
        
        return recovery_items
    
    async def _create_nutrition_section(self, nutrition_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create nutrition section in frontend-compatible format."""
        nutrition = {
            "goal": nutrition_plan.get("nutritional_goals", "Support overall health and fitness goals"),
            "calories": nutrition_plan.get("calorie_target", "Maintenance calories"),
            "protein": nutrition_plan.get("protein_target", "1.6-2.2 g/kg/day"),
            "carbohydrate": nutrition_plan.get("carb_target", "3-6 g/kg/day"),
            "fat": nutrition_plan.get("fat_target", "0.6-1.0 g/kg/day"),
            "timing_and_training_day_setup": nutrition_plan.get("meal_timing", [
                "Eat every 3-4 hours to maintain stable energy levels",
                "Include protein and carbohydrates within 2 hours after exercise"
            ])
        }
        
        return nutrition
    
    async def _generate_overview(self, request, research_findings: Dict[str, Any]) -> str:
        """Generate plan overview."""
        
        overview_prompt = f"""
        Create a comprehensive overview for a {request.population} health plan.
        
        Goals: {list(request.goals)}
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
            This comprehensive {request.population} health plan is designed to help you achieve your goals of {list(request.goals)} over {request.timeline}.
            
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
        if safety_report.get("overall_safety") != "low_risk":
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
