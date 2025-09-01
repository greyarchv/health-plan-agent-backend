import asyncio
from typing import List, Dict, Any
from src.tools.base_tool import BaseTool
from src.utils.config import Config
import openai
import anthropic

class PubMedQueryTool(BaseTool):
    """Tool for querying research papers and guidelines."""
    
    def __init__(self):
        super().__init__(
            name="pubmed_query",
            description="Query research papers and extract evidence-based recommendations"
        )
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def execute(self, keywords: str, population: str = None) -> Dict[str, Any]:
        """Simulate PubMed query and extract relevant findings."""
        
        prompt = f"""
        You are a research assistant specializing in exercise science and health guidelines.
        
        Query: {keywords}
        Population: {population or "general"}
        
        Please provide evidence-based recommendations based on current research. Include:
        1. Key findings from recent studies
        2. Current guidelines from reputable organizations (ACSM, WHO, etc.)
        3. Evidence level and confidence
        4. Practical recommendations
        5. Any contraindications or safety considerations
        
        Format your response as structured data.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )
            
            return {
                "query": keywords,
                "population": population,
                "findings": response.choices[0].message.content,
                "evidence_level": "A",
                "sources": ["Simulated research synthesis"]
            }
        except Exception as e:
            return {
                "error": f"Research query failed: {str(e)}",
                "findings": f"Unable to retrieve research for {keywords}. Please ensure OpenAI API key is configured correctly."
            }
    


class GuidelineExtractorTool(BaseTool):
    """Tool for extracting guidelines from healthcare organizations."""
    
    def __init__(self):
        super().__init__(
            name="guideline_extractor",
            description="Extract guidelines from healthcare organizations and professional bodies"
        )
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    
    async def execute(self, organization: str, topic: str) -> Dict[str, Any]:
        """Extract guidelines from specified organization."""
        
        prompt = f"""
        You are an expert in healthcare guidelines and recommendations.
        
        Organization: {organization}
        Topic: {topic}
        
        Please provide current guidelines and recommendations from this organization on the given topic.
        Include:
        1. Key recommendations
        2. Evidence basis
        3. Implementation guidelines
        4. Safety considerations
        5. Contraindications
        
        Format as structured recommendations.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=Config.ANTHROPIC_MODEL,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "organization": organization,
                "topic": topic,
                "guidelines": response.content[0].text,
                "last_updated": "2024",
                "confidence": "high"
            }
        except Exception as e:
            return {
                "error": f"Guideline extraction failed: {str(e)}",
                "fallback_guidelines": self._get_fallback_guidelines(organization, topic)
            }
    
    def _get_fallback_guidelines(self, organization: str, topic: str) -> Dict[str, Any]:
        """Provide fallback guidelines when API calls fail."""
        guidelines = {
            "ACSM": {
                "postpartum": "Begin exercise 6-8 weeks postpartum with medical clearance. Start with low-impact activities and gradually progress.",
                "weight_loss": "150-300 minutes moderate activity per week plus 2-3 strength training sessions.",
                "strength_training": "2-3 sessions per week targeting major muscle groups with progressive overload."
            },
            "WHO": {
                "general_fitness": "150 minutes moderate activity or 75 minutes vigorous activity per week plus muscle strengthening 2+ days per week."
            }
        }
        
        return {
            "guidelines": guidelines.get(organization, {}).get(topic, "General exercise guidelines apply."),
            "source": organization
        }

