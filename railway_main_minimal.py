"""
Minimal FastAPI app for testing Railway deployment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="Health Plan Agent Backend - Minimal",
    description="Minimal test version",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "message": "Minimal Health Plan Agent Backend is running",
        "version": "1.0.0"
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
        import asyncio
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=[{"role": "user", "content": "Give me a random word."}],
            max_tokens=10,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        
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
        "message": "Minimal Health Plan Agent Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "test_openai": "/api/v1/test/openai"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
