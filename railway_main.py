"""
Health Plan Agent Backend - Railway Deployment

FastAPI backend with integrated health-plan-agent for plan generation and management.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
import asyncio
from pathlib import Path

# Import the new simplified workout planners
try:
    print("🔍 Attempting to import IntegratedWorkoutPlanner...")
    from integrated_workout_planner import IntegratedWorkoutPlanner
    print("✅ IntegratedWorkoutPlanner imported successfully")
    
    print("🔍 Attempting to import SimpleWorkoutPlanner...")
    from simple_workout_planner import SimpleWorkoutPlanner
    print("✅ SimpleWorkoutPlanner imported successfully")
    
    PLANNERS_AVAILABLE = True
    print("✅ All new planners imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"❌ Error type: {type(e)}")
    import traceback
    print(f"❌ Full traceback: {traceback.format_exc()}")
    PLANNERS_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 Starting Health Plan Agent Backend...")
    
    # Initialize services if available
    if PLANNERS_AVAILABLE:
        try:
            print("🔍 Initializing IntegratedWorkoutPlanner...")
            app.state.integrated_planner = IntegratedWorkoutPlanner()
            print("✅ Integrated planner initialized successfully")
            
            print("🔍 Initializing SimpleWorkoutPlanner...")
            app.state.simple_planner = SimpleWorkoutPlanner()
            print("✅ Simple planner initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize planners: {e}")
            print(f"❌ Error type: {type(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            app.state.integrated_planner = None
            app.state.simple_planner = None
    else:
        app.state.integrated_planner = None
        app.state.simple_planner = None
        print("⚠️ Planners not available")
    
    print("✅ Health Plan Agent Backend is ready!")
    
    yield
    
    print("🛑 Shutting down Health Plan Agent Backend...")

# Create FastAPI app
app = FastAPI(
    title="Health Plan Agent Backend",
    description="Backend API for health plan generation and management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Health Plan Agent Backend is running",
        "version": "1.0.0"
    }

# Plan generation endpoint
@app.post("/api/v1/plans/generate")
async def generate_health_plan(request: dict):
    """Generate a new health plan using the new integrated workout planner"""
    try:
        print(f"🚀 Plan generation request received")
        print(f"📝 Request data: {request}")
        
        # Check if planners are available
        if not app.state.integrated_planner:
            print("❌ Integrated planner not available")
            raise HTTPException(status_code=503, detail="Integrated planner not available")
        
        # Extract user_id from request (for database storage)
        user_id = request.get('user_id', 'anonymous_user')
        
        # Prepare the request for the new planner
        planner_request = {
            'population': request.get('population', 'general'),
            'goals': request.get('goals', []),
            'constraints': request.get('constraints', []),
            'timeline': request.get('timeline', '12_weeks'),
            'fitness_level': request.get('fitness_level', 'intermediate'),
            'preferences': request.get('preferences', [])
        }
        
        print(f"📋 Structured request for {planner_request['population']}")
        print(f"📋 Goals: {planner_request['goals']}")
        print(f"📋 Timeline: {planner_request['timeline']}")
        print(f"📋 Fitness Level: {planner_request['fitness_level']}")
        
        # Generate the workout plan using the integrated planner
        print("🎯 Generating workout plan with integrated planner...")
        integrated_planner = app.state.integrated_planner
        
        # Use the integrated planner to generate and store the plan
        workout_plan = integrated_planner.generate_and_store_workout_plan(
            planner_request, 
            user_id=user_id
        )
        
        print(f"✅ Plan generated successfully!")
        print(f"📊 Plan ID: {workout_plan.get('plan_id')}")
        print(f"📊 Database ID: {workout_plan.get('database_id', 'Not stored in DB')}")
        
        return {
            "success": True,
            "message": "Workout plan generated and stored successfully",
            "data": {
                "plan_id": workout_plan.get('plan_id'),
                "database_id": workout_plan.get('database_id'),
                "user_id": user_id,
                "plan": workout_plan
            }
        }
            
    except Exception as e:
        print(f"❌ Error in plan generation: {str(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")

# Plan discovery endpoint
@app.get("/api/v1/plans/discover")
async def discover_plans():
    """Get all available health plans"""
    return {
        "success": True,
        "message": "Database not available in test mode",
        "data": {
            "plans": {},
            "total_plans": 0
        }
    }

# Get user plans endpoint
@app.get("/api/v1/plans/user/{user_id}")
async def get_user_plans(user_id: str):
    """Get all workout plans for a specific user"""
    try:
        if not app.state.integrated_planner:
            raise HTTPException(status_code=503, detail="Integrated planner not available")
        
        integrated_planner = app.state.integrated_planner
        user_plans = integrated_planner.get_user_plans(user_id)
        
        return {
            "success": True,
            "message": f"Retrieved {len(user_plans)} plans for user {user_id}",
            "data": {
                "user_id": user_id,
                "plans": user_plans,
                "total_plans": len(user_plans)
            }
        }
    except Exception as e:
        print(f"❌ Error retrieving user plans: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user plans: {str(e)}")

# Get specific plan endpoint
@app.get("/api/v1/plans/{plan_id}")
async def get_plan(plan_id: str):
    """Get a specific health plan by ID"""
    raise HTTPException(status_code=503, detail="Database not available in test mode")

# Test Supabase endpoint
@app.get("/api/v1/test/supabase")
async def test_supabase():
    """Test Supabase connectivity and table structure."""
    try:
        if not app.state.integrated_planner:
            return {
                "success": False,
                "error": "Integrated planner not available"
            }
        
        integrated_planner = app.state.integrated_planner
        
        if not integrated_planner.supabase:
            return {
                "success": False,
                "error": "Supabase not initialized"
            }
        
        # Test basic connection
        print("🔍 Testing Supabase connection...")
        
        # Try to query the workout_plans table
        try:
            result = integrated_planner.supabase.table("workout_plans").select("*").limit(1).execute()
            print(f"✅ Supabase connection successful")
            print(f"📊 Table query result: {len(result.data)} rows")
            
            return {
                "success": True,
                "message": "Supabase connection successful",
                "data": {
                    "table_exists": True,
                    "sample_rows": len(result.data),
                    "supabase_initialized": True
                }
            }
        except Exception as table_error:
            print(f"❌ Table query failed: {table_error}")
            return {
                "success": False,
                "error": f"Table query failed: {str(table_error)}",
                "data": {
                    "supabase_initialized": True,
                    "table_exists": False
                }
            }
        
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")
        return {
            "success": False,
            "error": f"Supabase test failed: {str(e)}"
        }

# Test OpenAI endpoint
@app.get("/api/v1/test/openai")
async def test_openai():
    """Test OpenAI API connectivity."""
    try:
        import openai
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        print(f"🔍 Testing OpenAI API connection...")
        print(f"🔑 API Key configured: {'Yes' if api_key else 'No'}")
        print(f"🔑 API Key length: {len(api_key) if api_key else 0}")
        print(f"🔑 API Key preview: {api_key[:10] if api_key else 'None'}...")
        
        if not api_key:
            return {
                "success": False,
                "error": "No OpenAI API key configured",
                "details": {
                    "api_key_configured": False,
                    "api_key_length": 0
                }
            }
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Make a simple test request
        print("📡 Making test request to OpenAI...")
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=[{"role": "user", "content": "Give me a random word."}],
            max_tokens=10,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API call successful!")
        print(f"📝 Response: '{result}'")
        
        return {
            "success": True,
            "message": "OpenAI API is working correctly!",
            "data": {
                "random_word": result,
                "model_used": response.model,
                "tokens_used": response.usage.total_tokens,
                "api_key_configured": True,
                "api_key_length": len(api_key),
                "api_key_preview": api_key[:10] + "..."
            }
        }
        
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        
        return {
            "success": False,
            "error": f"OpenAI API call failed: {str(e)}",
            "error_type": str(type(e)),
            "details": {
                "api_key_configured": bool(api_key),
                "api_key_length": len(api_key) if api_key else 0
            }
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Health Plan Agent Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_plan": "/api/v1/plans/generate",
            "get_user_plans": "/api/v1/plans/user/{user_id}",
            "discover_plans": "/api/v1/plans/discover",
            "get_plan": "/api/v1/plans/{plan_id}",
            "test_openai": "/api/v1/test/openai"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
