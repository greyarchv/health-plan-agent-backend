#!/usr/bin/env python3
"""
Test Backend Integration

This script tests the updated Railway backend with the new integrated workout planner.
"""

import requests
import json
import time

def test_backend_integration():
    """Test the updated backend integration."""
    
    print("🎯 Testing Updated Railway Backend Integration")
    print("=" * 60)
    
    # Base URL - update this to your Railway deployment URL
    # base_url = "http://localhost:8000"  # For local testing
    base_url = "https://web-production-f15a06.up.railway.app"  # For Railway deployment
    
    # Test 1: Health Check
    print("\n📋 Test 1: Health Check")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        print("   Make sure the backend is running locally or update the base_url")
        return
    
    # Test 2: Generate Workout Plan
    print("\n📋 Test 2: Generate Workout Plan")
    print("-" * 40)
    
    test_request = {
        "user_id": "test_user_123",
        "population": "muscle_building",
        "goals": ["hypertrophy", "strength_gain", "muscle_mass"],
        "constraints": ["none"],
        "timeline": "12_weeks",
        "fitness_level": "intermediate",
        "preferences": ["gym_based", "progressive_overload", "compound_movements"]
    }
    
    try:
        print(f"📤 Sending request: {test_request}")
        response = requests.post(
            f"{base_url}/api/v1/plans/generate",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Workout plan generated successfully!")
            print(f"   Plan ID: {result['data']['plan_id']}")
            print(f"   Database ID: {result['data'].get('database_id', 'Not stored in DB')}")
            print(f"   User ID: {result['data']['user_id']}")
            
            # Check if plan has the expected structure
            plan = result['data']['plan']
            required_keys = ['overview', 'weekly_split', 'global_rules', 'days', 'nutrition']
            missing_keys = [key for key in required_keys if key not in plan]
            
            if not missing_keys:
                print("✅ Plan structure is correct")
            else:
                print(f"⚠️ Missing plan keys: {missing_keys}")
            
            return result['data']['plan_id']
        else:
            print(f"❌ Plan generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Plan generation error: {e}")
        return None
    
    # Test 3: Get User Plans
    print("\n📋 Test 3: Get User Plans")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/v1/plans/user/test_user_123")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User plans retrieved successfully!")
            print(f"   Total plans: {result['data']['total_plans']}")
            print(f"   User ID: {result['data']['user_id']}")
        else:
            print(f"❌ Get user plans failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Get user plans error: {e}")
    
    # Test 4: Test OpenAI Connection
    print("\n📋 Test 4: Test OpenAI Connection")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/v1/test/openai")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ OpenAI connection test passed!")
                print(f"   Random word: {result['data']['random_word']}")
                print(f"   Model used: {result['data']['model_used']}")
            else:
                print(f"❌ OpenAI test failed: {result['error']}")
        else:
            print(f"❌ OpenAI test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ OpenAI test error: {e}")
    
    print(f"\n🎉 Backend integration test complete!")

def test_multiple_workout_types():
    """Test generating different types of workout plans."""
    
    print("\n🎯 Testing Multiple Workout Types")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    test_requests = [
        {
            "name": "Muscle Building",
            "request": {
                "user_id": "test_user_muscle",
                "population": "muscle_building",
                "goals": ["hypertrophy", "strength_gain"],
                "timeline": "12_weeks",
                "fitness_level": "intermediate"
            }
        },
        {
            "name": "Weight Loss",
            "request": {
                "user_id": "test_user_weight_loss",
                "population": "weight_loss",
                "goals": ["fat_loss", "muscle_preservation"],
                "timeline": "8_weeks",
                "fitness_level": "beginner"
            }
        },
        {
            "name": "Strength Training",
            "request": {
                "user_id": "test_user_strength",
                "population": "strength_training",
                "goals": ["maximal_strength", "power"],
                "timeline": "16_weeks",
                "fitness_level": "advanced"
            }
        }
    ]
    
    for i, test_case in enumerate(test_requests, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/plans/generate",
                json=test_case['request'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {test_case['name']} plan generated!")
                print(f"   Plan ID: {result['data']['plan_id']}")
                print(f"   User ID: {result['data']['user_id']}")
            else:
                print(f"❌ {test_case['name']} plan failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['name']} plan error: {e}")
    
    print(f"\n🎉 Multiple workout types test complete!")

if __name__ == "__main__":
    # Run the main integration test
    test_backend_integration()
    
    # Run the multiple workout types test
    test_multiple_workout_types()
