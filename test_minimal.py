#!/usr/bin/env python3
"""
Minimal test to verify basic functionality.
"""

import os
import sys
import asyncio
import openai
from dotenv import load_dotenv

async def test_openai_minimal():
    """Test OpenAI API with minimal setup."""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Testing OpenAI API connection (minimal)...")
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    print(f"🔑 API Key configured: {'Yes' if api_key else 'No'}")
    print(f"🔑 API Key length: {len(api_key) if api_key else 0}")
    print(f"🔑 API Key preview: {api_key[:10] if api_key else 'None'}...")
    print(f"🤖 Model: {model}")
    
    if not api_key:
        print("❌ No OpenAI API key found!")
        return False
    
    try:
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
    # Run the test
    success = asyncio.run(test_openai_minimal())
    
    if success:
        print("\n🎉 OpenAI API is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 OpenAI API test failed!")
        sys.exit(1)
