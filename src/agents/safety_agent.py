import asyncio
from typing import List, Dict, Any
from src.agents.base_agent import BaseAgent
from src.tools.validation_tools import ContraindicationCheckerTool, PlanValidatorTool
from src.utils.config import Config
import openai

class SafetyAgent(BaseAgent):
    """Agent responsible for validating plans for safety and contraindications."""
    
    def __init__(self):
        super().__init__(
            name="Safety Agent",
            description="Validates plans for contraindications and safety concerns"
        )
        
        # Add safety tools
        self.add_tool(ContraindicationCheckerTool())
        self.add_tool(PlanValidatorTool())
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def process(self, fitness_plan: Dict[str, Any], nutrition_plan: Dict[str, Any], 
                     motivation_plan: Dict[str, Any], constraints: List[str], 
                     research_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the complete health plan for safety."""
        
        safety_report = {
            "risk_assessment": {},
            "contraindications": [],
            "modifications": {},
            "emergency_protocols": [],
            "safety_recommendations": [],
            "validation_score": 0,
            "overall_safety": "pending"
        }
        
        # Extract exercises from fitness plan
        exercises = self._extract_exercises(fitness_plan)
        
        # Check for contraindications
        contraindication_check = await self._check_contraindications(exercises, constraints)
        safety_report["contraindications"] = contraindication_check["flagged_exercises"]
        safety_report["modifications"] = contraindication_check["safe_alternatives"]
        
        # Validate plan coherence
        plan_validation = await self._validate_plan_coherence({
            "fitness_component": fitness_plan,
            "nutrition_component": nutrition_plan,
            "motivation_component": motivation_plan
        })
        safety_report["validation_score"] = plan_validation["coherence_score"]
        
        # Assess overall risk
        risk_assessment = await self._assess_risk(constraints, contraindication_check, plan_validation)
        safety_report["risk_assessment"] = risk_assessment
        
        # Generate safety recommendations
        safety_recommendations = await self._generate_safety_recommendations(
            constraints, research_findings, contraindication_check
        )
        safety_report["safety_recommendations"] = safety_recommendations
        
        # Create emergency protocols
        emergency_protocols = await self._create_emergency_protocols(constraints, risk_assessment)
        safety_report["emergency_protocols"] = emergency_protocols
        
        # Determine overall safety rating
        safety_report["overall_safety"] = self._determine_safety_rating(safety_report)
        
        return safety_report
    
    def _extract_exercises(self, fitness_plan: Dict[str, Any]) -> List[str]:
        """Extract exercise names from fitness plan."""
        
        exercises = []
        
        if "exercises" in fitness_plan:
            for day, day_exercises in fitness_plan["exercises"].items():
                for exercise in day_exercises:
                    if isinstance(exercise, dict) and "name" in exercise:
                        exercises.append(exercise["name"])
                    elif isinstance(exercise, str):
                        exercises.append(exercise)
        
        return exercises
    
    async def _check_contraindications(self, exercises: List[str], constraints: List[str]) -> Dict[str, Any]:
        """Check exercises against contraindications."""
        
        contraindication_tool = self.get_tool("contraindication_checker")
        
        result = await contraindication_tool.execute(
            exercises=exercises,
            conditions=constraints
        )
        
        return result
    
    async def _validate_plan_coherence(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate plan coherence and logic."""
        
        validator_tool = self.get_tool("plan_validator")
        
        result = await validator_tool.execute(plan=plan)
        
        return result
    
    async def _assess_risk(self, constraints: List[str], contraindication_check: Dict[str, Any], 
                          plan_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level of the plan."""
        
        risk_factors = []
        risk_score = 0
        
        # Risk factors based on constraints
        high_risk_constraints = ["diastasis_recti", "pelvic_organ_prolapse", "pregnancy", "hypertension"]
        for constraint in constraints:
            if constraint in high_risk_constraints:
                risk_factors.append(f"High-risk condition: {constraint}")
                risk_score += 3
            else:
                risk_factors.append(f"Moderate-risk condition: {constraint}")
                risk_score += 1
        
        # Risk factors based on contraindications
        if contraindication_check["flagged_exercises"]:
            risk_factors.append(f"Contraindicated exercises: {len(contraindication_check['flagged_exercises'])}")
            risk_score += len(contraindication_check["flagged_exercises"]) * 2
        
        # Risk factors based on plan validation
        if plan_validation["coherence_score"] < 70:
            risk_factors.append("Low plan coherence score")
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 8:
            risk_level = "high"
        elif risk_score >= 4:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": self._get_risk_recommendations(risk_level, constraints)
        }
    
    async def _generate_safety_recommendations(self, constraints: List[str], 
                                             research_findings: Dict[str, Any],
                                             contraindication_check: Dict[str, Any]) -> List[str]:
        """Generate safety recommendations."""
        
        recommendations = []
        
        # Add research-based recommendations
        if research_findings.get("recommendations"):
            recommendations.extend(research_findings["recommendations"])
        
        # Add constraint-specific recommendations
        if "diastasis_recti" in constraints:
            recommendations.extend([
                "Monitor abdominal separation weekly",
                "Stop any exercise that causes doming",
                "Focus on transverse abdominis activation",
                "Consider working with a physical therapist"
            ])
        
        if "pelvic_organ_prolapse" in constraints:
            recommendations.extend([
                "Prioritize pelvic floor strengthening",
                "Avoid exercises that increase intra-abdominal pressure",
                "Consider working with a pelvic floor specialist",
                "Monitor for symptoms of prolapse"
            ])
        
        if "pregnancy" in constraints:
            recommendations.extend([
                "Get medical clearance before starting exercise",
                "Avoid exercises lying on back after 16 weeks",
                "Stay hydrated and avoid overheating",
                "Listen to your body and stop if needed"
            ])
        
        # Add general safety recommendations
        recommendations.extend([
            "Start slowly and progress gradually",
            "Stop if you experience pain or unusual symptoms",
            "Stay hydrated during exercise",
            "Get adequate rest and recovery",
            "Consult healthcare provider with any concerns"
        ])
        
        return recommendations
    
    async def _create_emergency_protocols(self, constraints: List[str], 
                                        risk_assessment: Dict[str, Any]) -> List[str]:
        """Create emergency protocols based on constraints and risk level."""
        
        protocols = []
        
        # General emergency protocols
        protocols.extend([
            "Stop exercise immediately if you experience chest pain, shortness of breath, or dizziness",
            "Seek medical attention for any severe pain or injury",
            "Call emergency services for any concerning symptoms"
        ])
        
        # Constraint-specific protocols
        if "diastasis_recti" in constraints:
            protocols.extend([
                "Stop immediately if you notice increased abdominal separation",
                "Seek medical attention if separation worsens or causes pain"
            ])
        
        if "pelvic_organ_prolapse" in constraints:
            protocols.extend([
                "Stop exercise if you experience pelvic pressure or heaviness",
                "Seek medical attention for any prolapse symptoms"
            ])
        
        if "pregnancy" in constraints:
            protocols.extend([
                "Stop exercise if you experience vaginal bleeding, contractions, or decreased fetal movement",
                "Seek immediate medical attention for any pregnancy-related concerns"
            ])
        
        if "hypertension" in constraints:
            protocols.extend([
                "Stop exercise if you experience severe headache, chest pain, or vision changes",
                "Monitor blood pressure regularly and report significant changes"
            ])
        
        # High-risk protocols
        if risk_assessment["risk_level"] == "high":
            protocols.extend([
                "Exercise with supervision when possible",
                "Have emergency contact information readily available",
                "Consider working with a qualified fitness professional"
            ])
        
        return protocols
    
    def _determine_safety_rating(self, safety_report: Dict[str, Any]) -> str:
        """Determine overall safety rating."""
        
        risk_level = safety_report["risk_assessment"].get("risk_level", "moderate")
        validation_score = safety_report.get("validation_score", 0)
        contraindications = len(safety_report.get("contraindications", []))
        
        if risk_level == "high" or validation_score < 50 or contraindications > 3:
            return "requires_medical_clearance"
        elif risk_level == "moderate" or validation_score < 70 or contraindications > 1:
            return "moderate_risk"
        else:
            return "low_risk"
    
    def _get_risk_recommendations(self, risk_level: str, constraints: List[str]) -> List[str]:
        """Get recommendations based on risk level."""
        
        recommendations = []
        
        if risk_level == "high":
            recommendations.extend([
                "Obtain medical clearance before starting",
                "Work with a qualified fitness professional",
                "Start with supervised sessions",
                "Monitor closely for adverse effects"
            ])
        elif risk_level == "moderate":
            recommendations.extend([
                "Consider medical consultation",
                "Start with low-intensity activities",
                "Progress slowly and carefully",
                "Monitor for any concerning symptoms"
            ])
        else:
            recommendations.extend([
                "Follow standard exercise guidelines",
                "Listen to your body",
                "Progress gradually",
                "Stay consistent with the plan"
            ])
        
        return recommendations

