"""
Health Plan Agent Backend - Railway Deployment

FastAPI backend with integrated health-plan-agent for plan generation and management.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

# Add src to path for health-plan-agent imports
sys.path.append(str(Path(__file__).parent / "src"))

from app.config import settings
from app.services.workout_plan_service import WorkoutPlanService
from src.agents.orchestrator_agent_fixed import OrchestratorAgentFixed
from src.utils.models import HealthPlanRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 Starting Health Plan Agent Backend...")
    print(f"🌍 Environment: {getattr(settings, 'RAILWAY_ENVIRONMENT', 'production')}")
    
    # Initialize services
    app.state.workout_service = WorkoutPlanService()
    app.state.orchestrator = OrchestratorAgentFixed()
    
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
async def generate_health_plan(request: HealthPlanRequest):
    """Generate a new health plan using the health-plan-agent system"""
    try:
        orchestrator = app.state.orchestrator
        health_plan = await orchestrator.generate_health_plan(request)
        
        # Store in database
        workout_service = app.state.workout_service
        plan_id = list(health_plan.keys())[0]  # Get the plan ID
        await workout_service.store_plan(plan_id, health_plan)
        
        return {
            "success": True,
            "message": "Health plan generated and stored successfully",
            "data": {
                "plan_id": plan_id,
                "plan": health_plan
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")

# Plan discovery endpoint
@app.get("/api/v1/plans/discover")
async def discover_plans():
    """Get all available health plans"""
    try:
        workout_service = app.state.workout_service
        plans = await workout_service.get_all_plans()
        
        return {
            "success": True,
            "message": "Plans discovered successfully",
            "data": {
                "plans": plans,
                "total_plans": len(plans)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discovering plans: {str(e)}")

# Get specific plan endpoint
@app.get("/api/v1/plans/{plan_id}")
async def get_plan(plan_id: str):
    """Get a specific health plan by ID"""
    try:
        workout_service = app.state.workout_service
        plan = await workout_service.get_plan(plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found")
        
        return {
            "success": True,
            "message": f"Plan '{plan_id}' retrieved successfully",
            "data": plan
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plan: {str(e)}")

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
            "discover_plans": "/api/v1/plans/discover",
            "get_plan": "/api/v1/plans/{plan_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
