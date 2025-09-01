import asyncio
from typing import List, Dict, Any
from .base_agent import BaseAgent
from ..utils.config import Config
import openai

class MotivationAgent(BaseAgent):
    """Agent responsible for designing motivation and goal-setting components."""
    
    def __init__(self):
        super().__init__(
            name="Motivation Agent",
            description="Develops goal-setting frameworks and encouragement systems"
        )
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def process(self, goals: List[str], timeline: str, fitness_level: str, 
                     constraints: List[str]) -> Dict[str, Any]:
        """Design motivation component based on goals and user profile."""
        
        motivation_plan = {
            "goal_setting": {},
            "progress_tracking": {},
            "encouragement_system": {},
            "habit_formation": {},
            "milestone_celebration": {}
        }
        
        # Design goal-setting framework
        goal_setting = await self._design_goal_setting(goals, timeline, fitness_level)
        motivation_plan["goal_setting"] = goal_setting
        
        # Design progress tracking system
        progress_tracking = await self._design_progress_tracking(goals, timeline)
        motivation_plan["progress_tracking"] = progress_tracking
        
        # Design encouragement system
        encouragement_system = await self._design_encouragement_system(goals, constraints)
        motivation_plan["encouragement_system"] = encouragement_system
        
        # Design habit formation strategies
        habit_formation = await self._design_habit_formation(goals, fitness_level)
        motivation_plan["habit_formation"] = habit_formation
        
        # Design milestone celebration system
        milestone_celebration = await self._design_milestone_celebration(timeline, goals)
        motivation_plan["milestone_celebration"] = milestone_celebration
        
        return motivation_plan
    
    async def _design_goal_setting(self, goals: List[str], timeline: str, 
                                 fitness_level: str) -> Dict[str, Any]:
        """Design goal-setting framework."""
        
        goal_setting = {
            "primary_goals": [],
            "secondary_goals": [],
            "process_goals": [],
            "outcome_goals": [],
            "goal_specificity": {},
            "goal_achievement_criteria": {}
        }
        
        # Define primary goals
        for goal in goals:
            goal_setting["primary_goals"].append({
                "goal": goal,
                "description": self._get_goal_description(goal),
                "timeline": timeline,
                "difficulty": fitness_level
            })
        
        # Define process goals (behavioral goals)
        process_goals = [
            "Complete 3 workout sessions per week",
            "Follow nutrition plan 80% of the time",
            "Get 7-9 hours of sleep per night",
            "Stay hydrated throughout the day"
        ]
        
        goal_setting["process_goals"] = process_goals
        
        # Define outcome goals (results-based goals)
        if "weight_loss" in goals:
            goal_setting["outcome_goals"].append("Lose 0.5-1 kg per week")
        if "strength_improvement" in goals:
            goal_setting["outcome_goals"].append("Increase strength by 5-10% over 12 weeks")
        if "core_restoration" in goals:
            goal_setting["outcome_goals"].append("Reduce diastasis recti separation by 50%")
        
        # Goal specificity framework
        goal_setting["goal_specificity"] = {
            "specific": "Clearly defined, measurable goals",
            "measurable": "Quantifiable progress indicators",
            "achievable": "Realistic for current fitness level",
            "relevant": "Aligned with overall health objectives",
            "time_bound": f"Timeline: {timeline}"
        }
        
        # Achievement criteria
        goal_setting["goal_achievement_criteria"] = {
            "consistency": "Maintain 80% adherence to plan",
            "progression": "Gradual improvement in performance",
            "safety": "No injuries or adverse effects",
            "sustainability": "Habits that can be maintained long-term"
        }
        
        return goal_setting
    
    async def _design_progress_tracking(self, goals: List[str], timeline: str) -> Dict[str, Any]:
        """Design progress tracking system."""
        
        progress_tracking = {
            "tracking_methods": [],
            "key_metrics": [],
            "assessment_frequency": {},
            "progress_indicators": {},
            "adjustment_triggers": []
        }
        
        # Tracking methods
        progress_tracking["tracking_methods"] = [
            "Weekly progress photos",
            "Body measurements",
            "Workout performance logs",
            "Nutrition adherence tracking",
            "Sleep and recovery monitoring"
        ]
        
        # Key metrics based on goals
        key_metrics = []
        if "weight_loss" in goals:
            key_metrics.extend(["Body weight", "Body measurements", "Progress photos"])
        if "strength_improvement" in goals:
            key_metrics.extend(["Lift progression", "Rep maxes", "Workout volume"])
        if "core_restoration" in goals:
            key_metrics.extend(["Diastasis measurement", "Core strength tests", "Functional movement"])
        
        progress_tracking["key_metrics"] = key_metrics
        
        # Assessment frequency
        progress_tracking["assessment_frequency"] = {
            "daily": ["Nutrition adherence", "Sleep quality", "Energy levels"],
            "weekly": ["Body weight", "Workout completion", "Progress photos"],
            "monthly": ["Body measurements", "Performance tests", "Goal review"]
        }
        
        # Progress indicators
        progress_tracking["progress_indicators"] = {
            "physical": ["Improved strength", "Better endurance", "Enhanced mobility"],
            "mental": ["Increased confidence", "Better stress management", "Improved mood"],
            "lifestyle": ["Better sleep", "More energy", "Improved nutrition habits"]
        }
        
        # Adjustment triggers
        progress_tracking["adjustment_triggers"] = [
            "Plateau for 2+ weeks",
            "Injury or pain",
            "Life circumstances change",
            "Goals evolve"
        ]
        
        return progress_tracking
    
    async def _design_encouragement_system(self, goals: List[str], constraints: List[str]) -> Dict[str, Any]:
        """Design encouragement and support system."""
        
        encouragement_system = {
            "positive_reinforcement": [],
            "motivational_messages": [],
            "support_resources": [],
            "challenge_management": {},
            "celebration_moments": []
        }
        
        # Positive reinforcement strategies
        encouragement_system["positive_reinforcement"] = [
            "Celebrate small wins daily",
            "Acknowledge consistency over perfection",
            "Focus on progress, not perfection",
            "Reward effort, not just outcomes"
        ]
        
        # Motivational messages
        encouragement_system["motivational_messages"] = [
            "Every workout makes you stronger",
            "Your future self will thank you",
            "Progress is progress, no matter how small",
            "You're building a healthier, stronger version of yourself"
        ]
        
        # Support resources
        encouragement_system["support_resources"] = [
            "Join online fitness communities",
            "Find an accountability partner",
            "Work with a personal trainer or coach",
            "Use fitness tracking apps for motivation"
        ]
        
        # Challenge management
        encouragement_system["challenge_management"] = {
            "setbacks": "View setbacks as learning opportunities, not failures",
            "plateaus": "Plateaus are normal - focus on consistency and trust the process",
            "motivation_dips": "Rely on discipline when motivation is low",
            "time_constraints": "Even 10 minutes of exercise is better than none"
        }
        
        # Celebration moments
        encouragement_system["celebration_moments"] = [
            "Completing your first week",
            "Achieving a new personal best",
            "Maintaining consistency for 30 days",
            "Reaching a milestone goal"
        ]
        
        return encouragement_system
    
    async def _design_habit_formation(self, goals: List[str], fitness_level: str) -> Dict[str, Any]:
        """Design habit formation strategies."""
        
        habit_formation = {
            "keystone_habits": [],
            "habit_stack_suggestions": [],
            "environment_design": {},
            "habit_tracking": {},
            "obstacle_planning": {}
        }
        
        # Keystone habits (habits that lead to other positive changes)
        habit_formation["keystone_habits"] = [
            "Morning routine with exercise",
            "Meal planning and preparation",
            "Consistent sleep schedule",
            "Regular movement throughout the day"
        ]
        
        # Habit stacking suggestions
        habit_formation["habit_stack_suggestions"] = [
            "After morning coffee → 10 minutes of stretching",
            "After lunch → 5-minute walk",
            "Before dinner → 15 minutes of core work",
            "Before bed → 5 minutes of meditation"
        ]
        
        # Environment design
        habit_formation["environment_design"] = {
            "home_workout_space": "Create a dedicated exercise area",
            "healthy_food_access": "Keep healthy snacks visible and accessible",
            "sleep_environment": "Optimize bedroom for quality sleep",
            "reminder_systems": "Use visual cues and reminders"
        }
        
        # Habit tracking
        habit_formation["habit_tracking"] = {
            "method": "Use habit tracker app or journal",
            "frequency": "Track daily habits",
            "review": "Weekly habit review and adjustment",
            "celebration": "Celebrate habit streaks"
        }
        
        # Obstacle planning
        habit_formation["obstacle_planning"] = {
            "common_obstacles": ["Lack of time", "Low energy", "Poor weather", "Travel"],
            "solutions": [
                "Have backup 10-minute workouts",
                "Prepare healthy meals in advance",
                "Have indoor workout alternatives",
                "Plan travel-friendly exercises"
            ]
        }
        
        return habit_formation
    
    async def _design_milestone_celebration(self, timeline: str, goals: List[str]) -> Dict[str, Any]:
        """Design milestone celebration system."""
        
        milestone_celebration = {
            "milestones": [],
            "celebration_ideas": [],
            "reflection_prompts": [],
            "next_goal_setting": {}
        }
        
        # Define milestones based on timeline
        if "12_weeks" in timeline:
            milestones = [
                {"week": 2, "milestone": "Establishing new habits"},
                {"week": 4, "milestone": "First month completed"},
                {"week": 6, "milestone": "Halfway point"},
                {"week": 8, "milestone": "Two-thirds complete"},
                {"week": 12, "milestone": "Program completion"}
            ]
        else:
            milestones = [
                {"week": 1, "milestone": "Getting started"},
                {"week": 2, "milestone": "Building momentum"},
                {"week": 4, "milestone": "One month strong"}
            ]
        
        milestone_celebration["milestones"] = milestones
        
        # Celebration ideas
        milestone_celebration["celebration_ideas"] = [
            "Treat yourself to a massage or spa day",
            "Buy new workout clothes or equipment",
            "Share your progress with friends and family",
            "Take progress photos and reflect on changes",
            "Plan a fun active outing"
        ]
        
        # Reflection prompts
        milestone_celebration["reflection_prompts"] = [
            "What have I learned about myself during this journey?",
            "What habits have I successfully established?",
            "What challenges did I overcome?",
            "How has my mindset changed?",
            "What am I most proud of?"
        ]
        
        # Next goal setting
        milestone_celebration["next_goal_setting"] = {
            "timing": "2 weeks before program completion",
            "process": "Reflect on current goals and set new ones",
            "considerations": [
                "Build on current progress",
                "Set new challenges",
                "Maintain sustainable habits",
                "Consider new areas for growth"
            ]
        }
        
        return milestone_celebration
    
    def _get_goal_description(self, goal: str) -> str:
        """Get description for a specific goal."""
        
        goal_descriptions = {
            "weight_loss": "Sustainably reduce body weight while preserving muscle mass",
            "muscle_gain": "Build lean muscle mass through progressive resistance training",
            "strength_improvement": "Increase maximal strength in key movement patterns",
            "endurance": "Improve cardiovascular fitness and work capacity",
            "core_restoration": "Restore core function and abdominal wall integrity",
            "pelvic_floor_recovery": "Strengthen pelvic floor muscles and improve function",
            "flexibility": "Improve joint mobility and muscle flexibility",
            "injury_prevention": "Build resilience and reduce injury risk"
        }
        
        return goal_descriptions.get(goal, "Improve overall health and fitness")

