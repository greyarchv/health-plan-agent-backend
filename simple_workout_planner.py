#!/usr/bin/env python3
"""
Simple Workout Planner - Direct OpenAI Approach

This bypasses the complex AG2 agent system and directly generates workout plans
using a simple, effective prompt to OpenAI.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

class SimpleWorkoutPlanner:
    """Simple, direct workout planner using OpenAI."""
    
    def __init__(self):
        """Initialize the simple workout planner."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_workout_plan(self, request: dict) -> dict:
        """Generate a workout plan using a direct OpenAI prompt."""
        
        print(f"🎯 Generating workout plan for {request['population']}")
        print(f"📋 Goals: {', '.join(request['goals'])}")
        
        # Create a comprehensive, direct prompt
        prompt = self._create_direct_prompt(request)
        
        try:
            # Make a single API call to generate the complete plan
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                                {
                "role": "system",
                "content": """You are an expert fitness trainer and nutritionist. Create comprehensive workout plans in EXACT JSON format matching the workout_plans.json structure.

CRITICAL: Output ONLY valid JSON with this EXACT structure (matching the provided workout_plans.json format):
{
  "overview": "Brief description of the plan",
  "weekly_split": ["Mon: Focus", "Tue: Focus", "Wed: Focus", "Thu: Focus", "Fri: Focus", "Sat: Focus", "Sun: Rest"],
  "global_rules": [
    {"title": "Effort", "text": "Keep 1-3 reps in reserve for most sets"},
    {"title": "Rest", "text": "2-3 min between compound sets, 60-90s for isolation"},
    {"title": "Tempo/ROM", "text": "Controlled eccentrics, full pain-free ROM"},
    {"title": "Progression", "text": "Double progression. Use the given rep range. When you hit the top of the range for all sets with the same load, increase load next time by the smallest increment"},
    {"title": "Volume tuning", "text": "If lifts stall for 2 consecutive weeks and you're sleeping 7-9h, add 1-2 sets for the lagging muscle. If performance or sleep drops, remove 2-4 weekly sets for that area"},
    {"title": "Deload", "text": "Every 5-6 weeks, reduce sets by ~30-50% and load by ~10-15% for one week"}
  ],
  "days": {
    "Day Name": [
      "1) Exercise name — 4×5–8",
      "2) Exercise name — 3×8–12",
      "3) Exercise name — 3×10–15"
    ]
  },
  "conditioning_and_recovery": [
    "Optional low-intensity cardio: 2×20–30 min easy pace on rest days or after lower-body days",
    "Mobility: 10–15 min daily movement prep and post-session resets for hips, T-spine, shoulders",
    "Sleep: 7–9 h/night. Keep a consistent schedule"
  ],
  "nutrition": {
    "goal": "Specific goal description",
    "calories": "Calorie guidance with specific recommendations",
    "protein": "1.6–2.2 g/kg/day. Split across 3–5 feedings. Aim 0.3–0.5 g/kg per meal from high-quality sources",
    "carbohydrate": "3–6 g/kg/day. Skew toward training window to fuel volume and recovery",
    "fat": "0.6–1.0 g/kg/day (generally 20–35% of calories). Fill remaining calories after protein and carbs",
    "timing_and_training_day_setup": [
      "2–3 h pre-workout: 0.5–1.0 g/kg carbs + 0.3 g/kg protein. Keep fats moderate",
      "30–60 min pre: Optional caffeine 1–3 mg/kg; add 1–2 g sodium in fluids if you sweat heavily",
      "Post-workout (within ~2 h): ~0.3 g/kg protein. Add 1–1.5 g/kg carbs across the next 3–6 h",
      "Pre-sleep: 30–40 g slow protein (e.g., casein or Greek yogurt) to support overnight MPS"
    ],
    "supplements": [
      "Creatine monohydrate: 3–5 g daily, any time",
      "Whey or casein: to hit protein targets",
      "Vitamin D3: 1000–2000 IU/day if intake or sun is low",
      "Fish oil: target 1–2 g EPA+DHA/day via supplements or fatty fish"
    ],
    "hydration_and_electrolytes": {
      "fluids": "30–40 ml/kg/day baseline, plus 500–1000 ml per hour of training",
      "electrolytes": "Include 2–3 g sodium/day minimum; more if you sweat heavily"
    }
  },
  "execution_checklist": [
    "Track loads, reps, and bodyweight. Aim to add 1–2 reps per exercise weekly or increase load when you hit the top of the range",
    "Keep most sets at 0–2 RIR; push isolation last sets to 0–1 RIR",
    "If joints feel beat up, swap barbell work for machine or DB variations while keeping volume and effort targets",
    "Reassess every 4–6 weeks. If a muscle lags, add 3–4 weekly sets for it and maintain for a block"
  ]
}

Output ONLY the JSON, no other text."""
            },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract the response content
            content = response.choices[0].message.content.strip()
            
            # Try to parse the JSON
            try:
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    workout_plan = json.loads(json_str)
                    
                    # Add metadata
                    workout_plan["plan_id"] = f"simple_workout_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    workout_plan["generation_method"] = "Direct_OpenAI_Prompt"
                    
                    print("✅ Workout plan generated successfully!")
                    return workout_plan
                else:
                    raise ValueError("No JSON found in response")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw response: {content[:200]}...")
                raise
                
        except Exception as e:
            print(f"❌ Error generating workout plan: {e}")
            raise
    
    def _create_direct_prompt(self, request: dict) -> str:
        """Create a direct, comprehensive prompt for workout plan generation."""
        
        population = request.get('population', 'general')
        goals = request.get('goals', [])
        constraints = request.get('constraints', [])
        timeline = request.get('timeline', '12_weeks')
        fitness_level = request.get('fitness_level', 'intermediate')
        preferences = request.get('preferences', [])
        
        prompt = f"""Create a comprehensive {timeline} workout plan for {population} with these requirements:

**Target Population**: {population}
**Primary Goals**: {', '.join(goals)}
**Health Constraints**: {', '.join(constraints) if constraints else 'None'}
**Timeline**: {timeline}
**Fitness Level**: {fitness_level}
**User Preferences**: {', '.join(preferences) if preferences else 'None'}

**Requirements**:
- Create a {timeline} program with progressive overload
- Include specific exercises with sets, reps, and rest intervals
- Address all safety concerns and contraindications
- Provide evidence-based training recommendations
- Include comprehensive nutrition and recovery guidance
- Make it practical and implementable

**Exercise Guidelines**:
- Use compound movements as primary exercises
- Include progressive overload principles
- Balance push/pull movements
- Include proper warm-up and cool-down
- Consider recovery and rest periods

**Nutrition Guidelines**:
- Provide specific macro targets
- Include timing recommendations
- Address supplementation if appropriate
- Consider the specific goals and timeline

Output the complete workout plan in the exact JSON format specified above."""
        
        return prompt

# Test the simple planner
def test_simple_planner():
    """Test the simple workout planner."""
    
    print("🎯 Testing Simple Workout Planner")
    print("=" * 50)
    
    try:
        # Create the planner
        planner = SimpleWorkoutPlanner()
        
        # Define muscle building request
        request = {
            "population": "muscle_building",
            "goals": ["hypertrophy", "strength_gain", "muscle_mass"],
            "constraints": ["none"],
            "timeline": "12_weeks",
            "fitness_level": "intermediate",
            "preferences": ["gym_based", "progressive_overload", "compound_movements"]
        }
        
        print(f"📋 Request: {request}")
        print("\n🚀 Generating workout plan...")
        
        # Generate the plan
        workout_plan = planner.generate_workout_plan(request)
        
        # Save the plan
        filename = "simple_muscle_building_plan.json"
        with open(filename, 'w') as f:
            json.dump(workout_plan, f, indent=2)
        
        print(f"\n✅ Plan saved to {filename}")
        
        # Show plan summary
        print(f"\n📊 Generated Plan Summary:")
        print(f"   Plan ID: {workout_plan.get('plan_id', 'Unknown')}")
        print(f"   Generation Method: {workout_plan.get('generation_method', 'Unknown')}")
        
        # Check components
        required_components = ["overview", "weekly_split", "global_rules", "days", "conditioning_and_recovery", "nutrition", "execution_checklist"]
        
        print(f"\n🔍 Plan Component Analysis:")
        for component in required_components:
            if component in workout_plan:
                content = workout_plan[component]
                if isinstance(content, list):
                    print(f"   ✅ {component}: Present ({len(content)} items)")
                elif isinstance(content, dict):
                    print(f"   ✅ {component}: Present ({len(content)} keys)")
                else:
                    print(f"   ✅ {component}: Present ({type(content).__name__})")
            else:
                print(f"   ❌ {component}: Missing")
        
        # Show preview
        if "overview" in workout_plan:
            print(f"\n📝 Overview: {workout_plan['overview'][:100]}...")
        
        if "weekly_split" in workout_plan and workout_plan["weekly_split"]:
            print(f"\n📅 Weekly Split:")
            for i, day in enumerate(workout_plan["weekly_split"], 1):
                print(f"   {i}. {day}")
        
        print(f"\n💾 Plan saved to: {filename}")
        print(f"🎉 Simple planner test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_planner()
