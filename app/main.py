"""
Slate AI Health Platform - Main Application

Full production version with database, AI, and all features.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
import os

from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 Starting Slate AI Health Platform...")
    print(f"🌍 Environment: {settings.RAILWAY_ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    
    # Try to initialize database (but don't fail if it doesn't work)
    try:
        from .database import sync_engine, Base
        print(f"🔍 Attempting to connect to database...")
        print(f"🔍 Database URL: {settings.DATABASE_URL[:50]}...")  # Show first 50 chars for security
        
        # Test connection first
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test successful")
        
        Base.metadata.create_all(bind=sync_engine)
        print("✅ Database tables created successfully")
        app.state.database_available = True
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print(f"⚠️  Error type: {type(e).__name__}")
        print("⚠️  Server will start but database features may not work properly")
        app.state.database_available = False
    
    # Test OpenAI connection (optional)
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.models.list()
            print("✅ OpenAI API connection successful!")
            app.state.openai_available = True
        except Exception as e:
            print(f"⚠️  OpenAI API connection failed: {e}")
            print("⚠️  Server will start but AI features may not work properly")
            app.state.openai_available = False
    else:
        print("⚠️  No valid OpenAI API key provided - AI features will be disabled")
        app.state.openai_available = False
    
    print("✅ Slate AI Health Platform is ready! (v1.1.5 - Complete Chat Flow - ROLLBACK VERSION)")
    
    yield
    
    print("🛑 Shutting down Slate AI Health Platform...")

# Create FastAPI app
app = FastAPI(
    title="Slate AI Health Platform",
    description="Personalized fitness and nutrition coaching platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware with production-ready settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (but don't fail if they don't load)
print("🔍 Loading API routers...")

# Load each router individually to handle failures gracefully
routers_loaded = 0
total_routers = 5

try:
    print("  🔍 Importing auth router...")
    from .routes import auth
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    print("  ✅ Auth router loaded")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Auth router failed to load: {e}")

# Chat router removed - using simplified SimpleChatView instead

try:
    print("  🔍 Importing workouts router...")
    from .routes import workouts
    app.include_router(workouts.router, prefix="/api/v1/workout", tags=["workouts"])
    print("  ✅ Workouts router loaded")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Workouts router failed to load: {e}")

try:
    print("  🔍 Importing nutrition router...")
    from .routes import nutrition
    app.include_router(nutrition.router, prefix="/api/v1/nutrition", tags=["nutrition"])
    print("  ✅ Nutrition router loaded")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Nutrition router failed to load: {e}")

try:
    print("  🔍 Importing users router...")
    from .routes import users
    app.include_router(users.router, prefix="/api/v1/user", tags=["users"])
    print("  ✅ Users router loaded")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Users router failed to load: {e}")

try:
    print("  🔍 Importing plans router...")
    from .api import plans
    app.include_router(plans.router, prefix="/api/v1", tags=["workout_plans"])
    print("  ✅ Plans router loaded")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Plans router failed to load: {e}")

if routers_loaded == total_routers:
    print("✅ All routers loaded successfully")
else:
    print(f"⚠️  {routers_loaded}/{total_routers} routers loaded successfully")
    print("⚠️  Server will start but some endpoints may not work")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Slate AI Health Platform",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.RAILWAY_ENVIRONMENT,
        "database_available": getattr(app.state, 'database_available', False),
        "openai_available": getattr(app.state, 'openai_available', False)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Slate AI Health Platform is running",
        "environment": settings.RAILWAY_ENVIRONMENT,
        "database_available": getattr(app.state, 'database_available', False),
        "openai_available": getattr(app.state, 'openai_available', False)
    }

@app.get("/test")
async def test():
    """Test endpoint"""
    return {"test": "success"}

@app.get("/status")
async def status():
    """Detailed status endpoint"""
    return {
        "status": "running",
        "environment": settings.RAILWAY_ENVIRONMENT,
        "database_available": getattr(app.state, 'database_available', False),
        "openai_available": getattr(app.state, 'openai_available', False),
        "routers_loaded": routers_loaded,
        "total_routers": total_routers
    }

@app.get("/callback")
async def callback(code: str = None, error: str = None):
    """Simple auth callback endpoint for Google OAuth"""
    if error:
        return {"error": error}
    
    if not code:
        return {"error": "No authorization code provided"}
    
    # For web-based OAuth, we need to return a simple HTML page
    # that the iOS app can extract the code from
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Slate Auth Callback</title>
    </head>
    <body>
        <script>
            // Send the authorization code to the iOS app
            window.location.href = "slate://auth/callback?code={code}";
        </script>
        <p>Processing authentication...</p>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) # Force deployment update
# Updated version for Railway deployment
VERSION = '1.1.6 - Complete Workout Flow'
