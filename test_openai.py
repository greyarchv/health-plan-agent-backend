#!/usr/bin/env python3
"""
Simple test to verify OpenAI API connectivity in Railway deployment.
"""

import os
import sys
import asyncio
import openai
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(str(os.path.dirname(__file__) / "src"))

from src.utils.config import Config

async def test_openai_connection():
    """Test OpenAI API connection with a simple request."""
    
    print("🔍 Testing OpenAI API connection...")
    print(f"🔑 API Key configured: {'Yes' if Config.OPENAI_API_KEY else 'No'}")
    print(f"🔑 API Key length: {len(Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else 0}")
    print(f"🔑 API Key preview: {Config.OPENAI_API_KEY[:10] if Config.OPENAI_API_KEY else 'None'}...")
    print(f"🤖 Model: {Config.OPENAI_MODEL}")
    
    if not Config.OPENAI_API_KEY:
        print("❌ No OpenAI API key found!")
        return False
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Make a simple test request
        print("📡 Making test request to OpenAI...")
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": "Give me a random word."}],
            max_tokens=10,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API call successful!")
        print(f"📝 Response: '{result}'")
        print(f"🔧 Model used: {response.model}")
        print(f"💰 Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    success = asyncio.run(test_openai_connection())
    
    if success:
        print("\n🎉 OpenAI API is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 OpenAI API test failed!")
        sys.exit(1)
