import asyncio
from typing import List, Dict, Any
from src.tools.base_tool import BaseTool
from src.utils.config import Config
import openai

class ContraindicationCheckerTool(BaseTool):
    """Tool for checking exercise contraindications."""
    
    def __init__(self):
        super().__init__(
            name="contraindication_checker",
            description="Check for contraindications and safety issues in exercise plans"
        )
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Contraindication database
        self.contraindications = {
            "diastasis_recti": [
                "Traditional crunches",
                "Sit-ups",
                "Russian twists",
                "Planks (if separation >2cm)",
                "Heavy lifting"
            ],
            "pelvic_organ_prolapse": [
                "Heavy lifting",
                "High-impact exercises",
                "Jumping",
                "Running",
                "Squats with heavy weights"
            ],
            "pregnancy": [
                "Contact sports",
                "Scuba diving",
                "Hot yoga",
                "Exercises lying on back after 16 weeks",
                "High-impact activities"
            ],
            "hypertension": [
                "Heavy lifting",
                "Isometric exercises",
                "High-intensity intervals",
                "Exercises with breath holding"
            ]
        }
    
    async def execute(self, exercises: List[str], conditions: List[str]) -> Dict[str, Any]:
        """Check exercises against contraindications."""
        
        flagged_exercises = []
        safe_alternatives = []
        
        for condition in conditions:
            contraindicated_exercises = self.contraindications.get(condition, [])
            
            for exercise in exercises:
                if exercise in contraindicated_exercises:
                    flagged_exercises.append({
                        "exercise": exercise,
                        "condition": condition,
                        "risk_level": "high"
                    })
        
        # Generate safe alternatives if needed
        if flagged_exercises:
            safe_alternatives = await self._generate_alternatives(conditions)
        
        return {
            "flagged_exercises": flagged_exercises,
            "safe_alternatives": safe_alternatives,
            "overall_risk": "high" if flagged_exercises else "low",
            "recommendations": self._get_safety_recommendations(conditions)
        }
    
    async def _generate_alternatives(self, conditions: List[str]) -> List[Dict[str, str]]:
        """Generate safe exercise alternatives."""
        
        alternatives = {
            "diastasis_recti": [
                {"original": "Crunches", "alternative": "Pelvic tilts"},
                {"original": "Sit-ups", "alternative": "Dead bug"},
                {"original": "Planks", "alternative": "Bird dog"}
            ],
            "pelvic_organ_prolapse": [
                {"original": "Heavy lifting", "alternative": "Light resistance training"},
                {"original": "Jumping", "alternative": "Walking"},
                {"original": "Running", "alternative": "Swimming"}
            ]
        }
        
        all_alternatives = []
        for condition in conditions:
            all_alternatives.extend(alternatives.get(condition, []))
        
        return all_alternatives
    
    def _get_safety_recommendations(self, conditions: List[str]) -> List[str]:
        """Get safety recommendations for conditions."""
        
        recommendations = {
            "diastasis_recti": [
                "Focus on transverse abdominis activation",
                "Avoid exercises that cause doming",
                "Progress gradually with core work"
            ],
            "pelvic_organ_prolapse": [
                "Prioritize pelvic floor strengthening",
                "Avoid exercises that increase intra-abdominal pressure",
                "Consider working with a pelvic floor physical therapist"
            ]
        }
        
        all_recommendations = []
        for condition in conditions:
            all_recommendations.extend(recommendations.get(condition, []))
        
        return all_recommendations

class PlanValidatorTool(BaseTool):
    """Tool for validating plan coherence and logic."""
    
    def __init__(self):
        super().__init__(
            name="plan_validator",
            description="Validate that health plans are coherent and follow logical progression"
        )
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate plan coherence."""
        
        validation_results = {
            "coherence_score": 0,
            "issues": [],
            "recommendations": [],
            "overall_assessment": "pending"
        }
        
        # Check fitness component
        if "fitness_component" in plan:
            fitness_validation = await self._validate_fitness(plan["fitness_component"])
            validation_results["issues"].extend(fitness_validation["issues"])
            validation_results["recommendations"].extend(fitness_validation["recommendations"])
        
        # Check nutrition component
        if "nutrition_component" in plan:
            nutrition_validation = await self._validate_nutrition(plan["nutrition_component"])
            validation_results["issues"].extend(nutrition_validation["issues"])
            validation_results["recommendations"].extend(nutrition_validation["recommendations"])
        
        # Calculate coherence score
        validation_results["coherence_score"] = self._calculate_coherence_score(validation_results["issues"])
        validation_results["overall_assessment"] = self._get_assessment(validation_results["coherence_score"])
        
        return validation_results
    
    async def _validate_fitness(self, fitness_component: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fitness component."""
        
        issues = []
        recommendations = []
        
        # Check for progressive overload
        if "progression" not in fitness_component:
            issues.append("Missing progression model")
            recommendations.append("Include progressive overload scheme")
        
        # Check exercise variety
        if "exercises" in fitness_component:
            exercise_days = len(fitness_component["exercises"])
            if exercise_days < 2:
                issues.append("Insufficient exercise frequency")
                recommendations.append("Include at least 2-3 training days per week")
        
        return {"issues": issues, "recommendations": recommendations}
    
    async def _validate_nutrition(self, nutrition_component: Dict[str, Any]) -> Dict[str, Any]:
        """Validate nutrition component."""
        
        issues = []
        recommendations = []
        
        # Check for essential components
        required_fields = ["calories", "protein", "carbohydrate", "fat"]
        for field in required_fields:
            if field not in nutrition_component:
                issues.append(f"Missing {field} information")
                recommendations.append(f"Include {field} recommendations")
        
        return {"issues": issues, "recommendations": recommendations}
    
    def _calculate_coherence_score(self, issues: List[str]) -> int:
        """Calculate coherence score based on issues found."""
        
        base_score = 100
        deduction_per_issue = 10
        
        return max(0, base_score - (len(issues) * deduction_per_issue))
    
    def _get_assessment(self, score: int) -> str:
        """Get assessment based on coherence score."""
        
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"

