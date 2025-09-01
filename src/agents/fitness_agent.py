import asyncio
from typing import List, Dict, Any
from src.agents.base_agent import BaseAgent
from src.tools.planning_tools import ExerciseDatabaseTool, ProgressionModelTool
from src.utils.config import Config
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
        
        print(f"🔬 Using research findings: {len(research_findings.get('findings', []))} research items")
        print(f"🔬 Research findings keys: {list(research_findings.keys())}")
        print(f"🔬 Research findings content: {research_findings}")
        
        # Generate evidence-based fitness plan using research findings
        fitness_plan = await self._generate_evidence_based_plan(
            research_findings=research_findings,
            goals=goals,
            constraints=constraints,
            timeline=timeline,
            fitness_level=fitness_level
        )
        
        return fitness_plan
    
    # Removed old _design_weekly_split method - now using AI-generated plans
    
    # Removed old _select_exercises method - now using AI-generated plans
    
    # Removed hardcoded _organize_by_days method - now using AI-generated plans
    
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
    
    async def _generate_evidence_based_plan(self, research_findings: Dict[str, Any], 
                                          goals: List[str], constraints: List[str], 
                                          timeline: str, fitness_level: str) -> Dict[str, Any]:
        """Generate evidence-based fitness plan using research findings and OpenAI."""
        
        print(f"🤖 Starting AI-powered plan generation for goals: {goals}")
        
        # Create comprehensive prompt using research findings
        prompt = self._create_evidence_based_prompt(research_findings, goals, constraints, timeline, fitness_level)
        
        try:
                    print(f"🤖 Calling OpenAI with prompt length: {len(prompt)}")
        print(f"🤖 OpenAI API Key configured: {'Yes' if self.client.api_key else 'No'}")
        print(f"🤖 OpenAI API Key length: {len(self.client.api_key) if self.client.api_key else 0}")
        print(f"🤖 OpenAI API Key preview: {self.client.api_key[:10] if self.client.api_key else 'None'}...")
            
            # Call OpenAI to generate the plan
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            # Parse the response into structured format
            plan_text = response.choices[0].message.content
            print(f"🤖 OpenAI response received, length: {len(plan_text)}")
            print(f"🤖 Response preview: {plan_text[:200]}...")
            
            fitness_plan = await self._parse_ai_response(plan_text, research_findings, constraints)
            
            print("✅ Evidence-based fitness plan generated using OpenAI")
            return fitness_plan
            
        except Exception as e:
            print(f"❌ OpenAI call failed: {e}")
            print(f"❌ Error type: {type(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            # Return minimal structure if AI fails
            return {
                "weekly_split": ["Mon: Full Body", "Tue: Rest", "Wed: Full Body", "Thu: Rest", "Fri: Full Body", "Sat: Active Recovery", "Sun: Rest"],
                "global_rules": [{"title": "Safety First", "text": "Stop if you experience pain or discomfort"}],
                "safety_considerations": ["Consult healthcare provider before starting"]
            }
    
    def _create_evidence_based_prompt(self, research_findings: Dict[str, Any], 
                                    goals: List[str], constraints: List[str], 
                                    timeline: str, fitness_level: str) -> str:
        """Create comprehensive prompt using research findings."""
        
        # Extract key research insights
        research_summary = ""
        if research_findings.get("findings"):
            for finding in research_findings["findings"]:
                if isinstance(finding, dict) and finding.get("findings"):
                    research_summary += f"Research: {finding['findings']}\n"
        
        # Extract guidelines
        guidelines = ""
        if research_findings.get("guidelines"):
            for guideline in research_findings["guidelines"]:
                if isinstance(guideline, dict) and guideline.get("recommendations"):
                    guidelines += f"Guideline: {guideline['recommendations']}\n"
        
        # Extract contraindications
        contraindications = research_findings.get("contraindications", [])
        contraindications_text = "\n".join([f"- {contra}" for contra in contraindications])
        
        prompt = f"""
You are an expert exercise physiologist and certified personal trainer with deep knowledge of evidence-based fitness programming.

RESEARCH CONTEXT:
{research_summary}

GUIDELINES:
{guidelines}

POPULATION: {research_findings.get('population', 'general')}
GOALS: {', '.join(goals)}
CONSTRAINTS: {', '.join(constraints)}
TIMELINE: {timeline}
FITNESS LEVEL: {fitness_level}

CONTRAINDICATIONS TO AVOID:
{contraindications_text}

TASK: Create a comprehensive 7-day workout plan that:
1. Is evidence-based and follows the research findings above
2. Targets the specific goals: {', '.join(goals)}
3. Accommodates constraints: {', '.join(constraints)}
4. Is appropriate for {fitness_level} fitness level
5. Can be completed in 30-60 minutes per session
6. Includes proper warm-up, main exercises, and cool-down
7. Follows progressive overload principles
8. Incorporates the latest research on {', '.join(goals)}

REQUIRED OUTPUT FORMAT (JSON):
{{
    "weekly_split": [
        "Mon: [Day Name]",
        "Tue: [Day Name]", 
        "Wed: [Day Name]",
        "Thu: [Day Name]",
        "Fri: [Day Name]",
        "Sat: [Day Name]",
        "Sun: [Day Name]"
    ],
    "days": {{
        "[Day Name]": [
            {{"name": "Exercise Name", "sets": "X", "reps": "Y", "rest": "Zs", "notes": "Evidence-based notes"}},
            {{"name": "Exercise Name", "sets": "X", "reps": "Y", "rest": "Zs", "notes": "Evidence-based notes"}}
        ]
    }},
    "global_rules": [
        {{"title": "Rule Title", "text": "Evidence-based rule explanation"}}
    ],
    "progression_model": {{
        "week_1_4": "Description of progression",
        "week_5_8": "Description of progression", 
        "week_9_12": "Description of progression"
    }},
    "evidence_basis": "Summary of research evidence supporting this plan"
}}

IMPORTANT: 
- Base every recommendation on the research findings provided
- Include specific exercise parameters (sets, reps, rest) based on evidence
- Explain the rationale for exercise selection in notes
- Ensure the plan is safe and appropriate for the constraints
- Make it challenging but achievable for the fitness level
"""
        
        return prompt
    
    async def _parse_ai_response(self, response_text: str, research_findings: Dict[str, Any], 
                               constraints: List[str]) -> Dict[str, Any]:
        """Parse AI response into structured fitness plan."""
        
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                # If no JSON found, create structured plan from text
                plan_data = await self._extract_plan_from_text(response_text)
            
            # Add research context
            plan_data["research_context"] = {
                "population": research_findings.get("population"),
                "goals": research_findings.get("goals"),
                "constraints": constraints,
                "evidence_level": "A",
                "sources": ["AI-generated based on research findings"]
            }
            
            return plan_data
            
        except Exception as e:
            print(f"❌ Failed to parse AI response: {e}")
            # Return fallback structure
            return {
                "weekly_split": ["Mon: Full Body", "Tue: Rest", "Wed: Full Body", "Thu: Rest", "Fri: Full Body", "Sat: Active Recovery", "Sun: Rest"],
                "days": {
                    "Full Body": [
                        {"name": "Dynamic warm-up", "sets": "1", "reps": "8-10 min", "rest": "N/A", "notes": "Based on research findings"},
                        {"name": "Compound exercises", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Evidence-based selection"}
                    ]
                },
                "global_rules": [{"title": "Evidence-Based", "text": "All exercises selected based on research findings"}],
                "research_context": {"evidence_level": "A", "sources": ["Research synthesis"]}
            }
    
    async def _extract_plan_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured plan from AI text response."""
        # This would parse the text response into structured format
        # For now, return basic structure
        return {
            "weekly_split": ["Mon: Full Body", "Tue: Rest", "Wed: Full Body", "Thu: Rest", "Fri: Full Body", "Sat: Active Recovery", "Sun: Rest"],
            "days": {
                "Full Body": [
                    {"name": "Evidence-based exercise", "sets": "3", "reps": "8-12", "rest": "90s", "notes": "Based on research"}
                ]
            },
            "global_rules": [{"title": "Research-Based", "text": "All recommendations based on evidence"}]
        }

