from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

# Remove restrictive enums and use flexible string types
class HealthPlanRequest(BaseModel):
    """Request model for health plan generation."""
    population: str = Field(..., description="Target population (e.g., 'senior_fitness', 'athletes', 'beginners', 'postpartum_mothers')")
    goals: List[str] = Field(..., description="Health and fitness goals (e.g., 'mobility', 'strength', 'weight_loss', 'endurance')")
    constraints: List[str] = Field(default_factory=list, description="Health constraints or conditions (e.g., 'arthritis', 'back_pain', 'diastasis_recti')")
    timeline: str = Field(default="12_weeks", description="Program timeline (e.g., '8_weeks', '12_weeks', '16_weeks')")
    preferences: List[str] = Field(default_factory=list, description="User preferences (e.g., 'home_workouts', 'gym_based', 'low_impact')")
    fitness_level: str = Field(default="beginner", description="Fitness level (e.g., 'beginner', 'intermediate', 'advanced')")
    equipment_available: List[str] = Field(default_factory=list, description="Available equipment (e.g., 'dumbbells', 'resistance_bands', 'none')")

class ResearchFinding(BaseModel):
    """Model for research findings."""
    topic: str
    evidence_level: str
    source: str
    summary: str
    recommendations: List[str]
    contraindications: List[str] = Field(default_factory=list)

class Exercise(BaseModel):
    """Model for individual exercises."""
    name: str
    category: str
    difficulty: str
    equipment: List[str]
    sets: str
    reps: str
    rest: str
    notes: Optional[str] = None

class FitnessComponent(BaseModel):
    """Model for fitness component of health plan."""
    weekly_split: List[str]
    exercises: Dict[str, List[Exercise]]
    progression: Dict[str, Any]
    global_rules: List[Dict[str, str]]

class NutritionComponent(BaseModel):
    """Model for nutrition component of health plan."""
    goal: str
    calories: str
    protein: str
    carbohydrate: str
    fat: str
    meal_timing: List[str]
    supplements: List[str]
    hydration: Dict[str, str]

class MotivationComponent(BaseModel):
    """Model for motivation component of health plan."""
    goal_setting: Dict[str, Any]
    progress_tracking: Dict[str, Any]
    encouragement_system: Dict[str, Any]

class SafetyReport(BaseModel):
    """Model for safety validation report."""
    risk_level: str
    contraindications: List[str]
    modifications: Dict[str, Any]
    emergency_protocols: List[str]

class HealthPlan(BaseModel):
    """Complete health plan model."""
    population: str
    overview: str
    research_basis: Dict[str, Any]
    fitness_component: FitnessComponent
    nutrition_component: NutritionComponent
    motivation_component: MotivationComponent
    safety_protocols: SafetyReport
    execution_checklist: List[str]

