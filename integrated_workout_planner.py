#!/usr/bin/env python3
"""
Integrated Workout Planner - OpenAI + Supabase

This combines the simple OpenAI workout planner with Supabase database integration
to generate and store workout plans in your database.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import openai
from supabase import create_client, Client

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

class IntegratedWorkoutPlanner:
    """Integrated workout planner with Supabase database storage."""
    
    def __init__(self):
        """Initialize the integrated workout planner."""
        # OpenAI setup
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Supabase setup
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            print("⚠️ Warning: Supabase credentials not found. Plans will be saved locally only.")
            self.supabase = None
        else:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Supabase connection established")
    
    def generate_and_store_workout_plan(self, request: dict, user_id: str = None) -> dict:
        """Generate a workout plan and store it in Supabase."""
        
        print(f"🎯 Generating workout plan for {request['population']}")
        print(f"📋 Goals: {', '.join(request['goals'])}")
        
        # Generate the workout plan
        workout_plan = self._generate_workout_plan(request)
        
        # Add metadata
        workout_plan["user_id"] = user_id
        workout_plan["created_at"] = datetime.now().isoformat()
        workout_plan["status"] = "active"
        
        # Store in Supabase if available
        if self.supabase:
            try:
                print(f"🔍 Attempting to store plan in Supabase...")
                print(f"🔍 Plan ID: {workout_plan.get('plan_id')}")
                print(f"🔍 User ID: {workout_plan.get('user_id')}")
                
                result = self._store_plan_in_supabase(workout_plan)
                workout_plan["database_id"] = result.get("id")
                print(f"✅ Plan stored in Supabase with ID: {result.get('id')}")
            except Exception as e:
                print(f"⚠️ Failed to store in Supabase: {e}")
                print(f"⚠️ Error type: {type(e)}")
                import traceback
                print(f"⚠️ Full traceback: {traceback.format_exc()}")
                print("💾 Plan will be saved locally only")
        
        # Always save locally as backup
        self._save_plan_locally(workout_plan)
        
        return workout_plan
    
    def _generate_workout_plan(self, request: dict) -> dict:
        """Generate a workout plan using OpenAI."""
        
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
                    workout_plan["plan_id"] = f"integrated_workout_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    workout_plan["generation_method"] = "Integrated_OpenAI_Supabase"
                    
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
    
    def _store_plan_in_supabase(self, workout_plan: dict) -> dict:
        """Store the workout plan in Supabase database."""
        
        if not self.supabase:
            raise ValueError("Supabase not initialized")
        
        # Prepare the data for Supabase - only include fields that exist in the plan
        supabase_data = {
            "plan_id": workout_plan.get("plan_id"),
            "user_id": workout_plan.get("user_id")
        }
        
        # Only add optional fields if they exist in the workout plan
        if "population" in workout_plan:
            supabase_data["population"] = workout_plan.get("population")
        if "goals" in workout_plan:
            supabase_data["goals"] = json.dumps(workout_plan.get("goals", []))
        if "timeline" in workout_plan:
            supabase_data["timeline"] = workout_plan.get("timeline")
        if "fitness_level" in workout_plan:
            supabase_data["fitness_level"] = workout_plan.get("fitness_level")
        if "generation_method" in workout_plan:
            supabase_data["generation_method"] = workout_plan.get("generation_method")
        
        # Always include the full plan data
        supabase_data["plan_data"] = json.dumps(workout_plan)
        
        print(f"🔍 Supabase data prepared: {list(supabase_data.keys())}")
        print(f"🔍 Plan ID: {supabase_data['plan_id']}")
        print(f"🔍 User ID: {supabase_data['user_id']}")
        
        # Insert into Supabase
        print(f"🔍 Attempting Supabase insert...")
        result = self.supabase.table("workout_plans").insert(supabase_data).execute()
        
        print(f"🔍 Supabase result: {result}")
        print(f"🔍 Result data: {result.data}")
        
        if result.data:
            print(f"✅ Supabase insert successful!")
            return result.data[0]
        else:
            print(f"❌ Supabase insert failed - no data returned")
            raise ValueError("Failed to insert into Supabase")
    
    def _save_plan_locally(self, workout_plan: dict):
        """Save the workout plan locally as a backup."""
        
        filename = f"backup_{workout_plan.get('plan_id', 'unknown')}.json"
        with open(filename, 'w') as f:
            json.dump(workout_plan, f, indent=2)
        
        print(f"💾 Plan saved locally as backup: {filename}")
    
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
    
    def get_user_plans(self, user_id: str) -> list:
        """Get all workout plans for a specific user."""
        
        if not self.supabase:
            print("⚠️ Supabase not available")
            return []
        
        try:
            result = self.supabase.table("workout_plans").select("*").eq("user_id", user_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Error fetching user plans: {e}")
            return []
    
    def update_plan_status(self, plan_id: str, status: str):
        """Update the status of a workout plan."""
        
        if not self.supabase:
            print("⚠️ Supabase not available")
            return
        
        try:
            result = self.supabase.table("workout_plans").update({"status": status}).eq("plan_id", plan_id).execute()
            print(f"✅ Plan {plan_id} status updated to {status}")
        except Exception as e:
            print(f"❌ Error updating plan status: {e}")

# Test the integrated planner
def test_integrated_planner():
    """Test the integrated workout planner."""
    
    print("🎯 Testing Integrated Workout Planner")
    print("=" * 50)
    
    try:
        # Create the planner
        planner = IntegratedWorkoutPlanner()
        
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
        print("\n🚀 Generating and storing workout plan...")
        
        # Generate and store the plan
        workout_plan = planner.generate_and_store_workout_plan(request, user_id="test_user_123")
        
        print(f"\n✅ Plan generated and stored successfully!")
        print(f"   Plan ID: {workout_plan.get('plan_id')}")
        print(f"   Database ID: {workout_plan.get('database_id', 'Not stored in DB')}")
        print(f"   User ID: {workout_plan.get('user_id')}")
        
        # Test fetching user plans
        print(f"\n🔍 Testing user plan retrieval...")
        user_plans = planner.get_user_plans("test_user_123")
        print(f"   Found {len(user_plans)} plans for user")
        
        print(f"\n🎉 Integrated planner test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integrated_planner()
