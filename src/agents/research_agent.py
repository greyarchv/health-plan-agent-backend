import asyncio
from typing import List, Dict, Any
from .base_agent import BaseAgent
from ..tools.research_tools import PubMedQueryTool, GuidelineExtractorTool
from ..utils.config import Config
import openai

class ResearchAgent(BaseAgent):
    """Agent responsible for gathering evidence-based research and guidelines."""
    
    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Gathers evidence from research papers and healthcare guidelines"
        )
        
        # Add research tools
        self.add_tool(PubMedQueryTool())
        self.add_tool(GuidelineExtractorTool())
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def process(self, population: str, goals: List[str], constraints: List[str] = None) -> Dict[str, Any]:
        """Gather research evidence for the given population and goals."""
        
        if constraints is None:
            constraints = []
        
        research_findings = {
            "population": population,
            "goals": goals,
            "constraints": constraints,
            "findings": [],
            "guidelines": [],
            "contraindications": [],
            "recommendations": []
        }
        
        # Query research for each goal
        for goal in goals:
            findings = await self._research_goal(population, goal)
            research_findings["findings"].append(findings)
        
        # Get guidelines from relevant organizations
        guidelines = await self._get_guidelines(population, goals)
        research_findings["guidelines"] = guidelines
        
        # Extract contraindications and safety considerations
        safety_info = await self._extract_safety_info(population, constraints)
        research_findings["contraindications"] = safety_info["contraindications"]
        research_findings["recommendations"] = safety_info["recommendations"]
        
        return research_findings
    
    async def _research_goal(self, population: str, goal: str) -> Dict[str, Any]:
        """Research a specific goal for the population."""
        
        pubmed_tool = self.get_tool("pubmed_query")
        
        # Create research query
        query = f"{population} {goal} exercise guidelines"
        
        findings = await pubmed_tool.execute(
            keywords=query,
            population=population
        )
        
        return {
            "goal": goal,
            "query": query,
            "findings": findings
        }
    
    async def _get_guidelines(self, population: str, goals: List[str]) -> List[Dict[str, Any]]:
        """Get guidelines from relevant healthcare organizations."""
        
        guideline_tool = self.get_tool("guideline_extractor")
        guidelines = []
        
        # Organizations to query
        organizations = ["ACSM", "WHO", "AHA"]
        
        for org in organizations:
            for goal in goals:
                guideline = await guideline_tool.execute(
                    organization=org,
                    topic=f"{population} {goal}"
                )
                guidelines.append(guideline)
        
        return guidelines
    
    async def _extract_safety_info(self, population: str, constraints: List[str]) -> Dict[str, Any]:
        """Extract safety information and contraindications."""
        
        safety_prompt = f"""
        For {population} population with constraints: {constraints}
        
        Please provide:
        1. List of contraindicated exercises or activities
        2. Safety considerations
        3. Recommended modifications
        4. Warning signs to watch for
        
        Format as structured safety guidelines.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": safety_prompt}],
                max_tokens=1000,
                temperature=Config.TEMPERATURE
            )
            
            # Parse safety information (simplified for demo)
            safety_info = {
                "contraindications": self._extract_contraindications(population, constraints),
                "recommendations": self._extract_recommendations(population, constraints)
            }
            
            return safety_info
        except Exception as e:
            return {
                "contraindications": [],
                "recommendations": ["Consult healthcare provider before starting any exercise program"]
            }
    
    def _extract_contraindications(self, population: str, constraints: List[str]) -> List[str]:
        """Extract contraindications based on population and constraints."""
        
        contraindications = {
            "postpartum_reconditioning": [
                "Unresolved diastasis recti >2cm",
                "Pelvic organ prolapse symptoms",
                "Uncontrolled bleeding",
                "C-section complications"
            ],
            "weight_loss": [
                "Severe obesity complications",
                "Uncontrolled hypertension",
                "Cardiac conditions"
            ]
        }
        
        base_contraindications = contraindications.get(population, [])
        
        # Add constraint-specific contraindications
        constraint_contraindications = {
            "diastasis_recti": ["Traditional crunches", "Sit-ups", "Heavy lifting"],
            "pelvic_organ_prolapse": ["High-impact exercises", "Heavy lifting"],
            "hypertension": ["Heavy lifting", "Isometric exercises"]
        }
        
        for constraint in constraints:
            if constraint in constraint_contraindications:
                base_contraindications.extend(constraint_contraindications[constraint])
        
        return list(set(base_contraindications))  # Remove duplicates
    
    def _extract_recommendations(self, population: str, constraints: List[str]) -> List[str]:
        """Extract safety recommendations."""
        
        recommendations = {
            "postpartum_reconditioning": [
                "Begin exercise 6-8 weeks postpartum with medical clearance",
                "Start with gentle walking and pelvic floor exercises",
                "Progress gradually and listen to your body",
                "Stop if you experience pain or unusual symptoms"
            ],
            "weight_loss": [
                "Start with low-impact activities",
                "Gradually increase intensity and duration",
                "Focus on sustainable lifestyle changes",
                "Monitor progress and adjust as needed"
            ]
        }
        
        return recommendations.get(population, ["Consult healthcare provider before starting"])

