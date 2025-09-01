#!/usr/bin/env python3
"""
Simple Health Plan Manager
Interact with the health-plan-agent backend API
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "https://web-production-f15a06.up.railway.app"

def generate_plan(population: str, goals: list, constraints: list = None, 
                 timeline: str = "12_weeks", fitness_level: str = "beginner") -> Dict[str, Any]:
    """Generate a new health plan"""
    
    payload = {
        "population": population,
        "goals": goals,
        "constraints": constraints or [],
        "timeline": timeline,
        "fitness_level": fitness_level
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/plans/generate", json=payload)
    response.raise_for_status()
    
    return response.json()

def list_plans() -> Dict[str, Any]:
    """Get all available plans"""
    response = requests.get(f"{BASE_URL}/api/v1/plans/discover")
    response.raise_for_status()
    return response.json()

def get_plan(plan_id: str) -> Dict[str, Any]:
    """Get a specific plan by ID"""
    response = requests.get(f"{BASE_URL}/api/v1/plans/{plan_id}")
    response.raise_for_status()
    return response.json()

def main():
    """Simple CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python plan_manager.py list                    # List all plans")
        print("  python plan_manager.py get <plan_id>          # Get specific plan")
        print("  python plan_manager.py generate <population> <goals...>  # Generate new plan")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "list":
            result = list_plans()
            plans = result["data"]["plans"]
            print(f"Found {len(plans)} plans:")
            for plan_id in plans.keys():
                print(f"  - {plan_id}")
        
        elif command == "get":
            if len(sys.argv) < 3:
                print("Usage: python plan_manager.py get <plan_id>")
                return
            plan_id = sys.argv[2]
            result = get_plan(plan_id)
            print(json.dumps(result, indent=2))
        
        elif command == "generate":
            if len(sys.argv) < 4:
                print("Usage: python plan_manager.py generate <population> <goal1> <goal2> ...")
                return
            population = sys.argv[2]
            goals = sys.argv[3:]
            result = generate_plan(population, goals)
            print(f"Generated plan: {result['data']['plan_id']}")
            print(json.dumps(result, indent=2))
        
        else:
            print(f"Unknown command: {command}")
    
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
