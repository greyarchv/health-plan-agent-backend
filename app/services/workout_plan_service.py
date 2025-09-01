"""
Workout Plan Service for Supabase operations
Handles storing, retrieving, and managing workout plans in the database
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from supabase import create_client, Client
from app.config import settings

class WorkoutPlanService:
    """Service for managing workout plans in Supabase."""
    
    def __init__(self):
        """Initialize the Supabase client."""
        # Use the settings instance directly
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        self.table_name = "workout_plans"
    
    async def store_plan(self, plan_id: str, plan_data: Dict[str, Any], 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store a workout plan in the database.
        
        Args:
            plan_id: Unique identifier for the plan
            plan_data: The workout plan data (frontend-compatible format)
            metadata: Optional metadata about the plan
            
        Returns:
            Dict containing the stored plan information
        """
        try:
            # Prepare the data for storage
            plan_record = {
                "plan_id": plan_id,
                "plan_data": plan_data,
                "metadata": metadata or {},
                "is_active": True
            }
            
            # Insert the plan into the database
            result = self.supabase.table(self.table_name).insert(plan_record).execute()
            
            if result.data:
                stored_plan = result.data[0]
                print(f"✅ Plan '{plan_id}' stored successfully in database")
                return {
                    "success": True,
                    "plan_id": stored_plan["plan_id"],
                    "id": stored_plan["id"],
                    "created_at": stored_plan["created_at"]
                }
            else:
                raise Exception("No data returned from insert operation")
                
        except Exception as e:
            print(f"❌ Error storing plan '{plan_id}': {str(e)}")
            raise Exception(f"Failed to store plan: {str(e)}")
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a workout plan from the database.
        
        Args:
            plan_id: Unique identifier for the plan
            
        Returns:
            The workout plan data or None if not found
        """
        try:
            result = self.supabase.table(self.table_name).select("*").eq("plan_id", plan_id).eq("is_active", True).execute()
            
            if result.data:
                plan_record = result.data[0]
                return plan_record["plan_data"]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving plan '{plan_id}': {str(e)}")
            return None
    
    async def get_all_plans(self) -> List[Dict[str, Any]]:
        """
        Retrieve all active workout plans from the database.
        
        Returns:
            List of all active workout plans
        """
        try:
            result = self.supabase.table(self.table_name).select("*").eq("is_active", True).order("created_at", desc=True).execute()
            
            if result.data:
                plans = {}
                for plan_record in result.data:
                    plan_id = plan_record["plan_id"]
                    plans[plan_id] = plan_record["plan_data"]
                
                return plans
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error retrieving all plans: {str(e)}")
            return {}
    
    async def get_plans_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Retrieve plans by category using metadata filtering.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of plans in the specified category
        """
        try:
            # Query using JSONB containment operator
            result = self.supabase.table(self.table_name).select("*").eq("is_active", True).contains("metadata", {"category": category}).execute()
            
            if result.data:
                plans = {}
                for plan_record in result.data:
                    plan_id = plan_record["plan_id"]
                    plans[plan_id] = plan_record["plan_data"]
                
                return plans
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error retrieving plans by category '{category}': {str(e)}")
            return {}
    
    async def update_plan(self, plan_id: str, plan_data: Dict[str, Any], 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing workout plan.
        
        Args:
            plan_id: Unique identifier for the plan
            plan_data: Updated workout plan data
            metadata: Optional updated metadata
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            update_data = {"plan_data": plan_data}
            if metadata:
                update_data["metadata"] = metadata
            
            result = self.supabase.table(self.table_name).update(update_data).eq("plan_id", plan_id).execute()
            
            if result.data:
                print(f"✅ Plan '{plan_id}' updated successfully")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error updating plan '{plan_id}': {str(e)}")
            return False
    
    async def deactivate_plan(self, plan_id: str) -> bool:
        """
        Deactivate a workout plan (soft delete).
        
        Args:
            plan_id: Unique identifier for the plan
            
        Returns:
            True if deactivation successful, False otherwise
        """
        try:
            result = self.supabase.table(self.table_name).update({"is_active": False}).eq("plan_id", plan_id).execute()
            
            if result.data:
                print(f"✅ Plan '{plan_id}' deactivated successfully")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error deactivating plan '{plan_id}': {str(e)}")
            return False
    
    async def delete_plan(self, plan_id: str) -> bool:
        """
        Permanently delete a workout plan from the database.
        
        Args:
            plan_id: Unique identifier for the plan
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            result = self.supabase.table(self.table_name).delete().eq("plan_id", plan_id).execute()
            
            if result.data:
                print(f"✅ Plan '{plan_id}' deleted successfully")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error deleting plan '{plan_id}': {str(e)}")
            return False
    
    async def plan_exists(self, plan_id: str) -> bool:
        """
        Check if a plan exists in the database.
        
        Args:
            plan_id: Unique identifier for the plan
            
        Returns:
            True if plan exists, False otherwise
        """
        try:
            result = self.supabase.table(self.table_name).select("plan_id").eq("plan_id", plan_id).eq("is_active", True).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"❌ Error checking if plan '{plan_id}' exists: {str(e)}")
            return False
    
    async def get_plan_metadata(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific plan.
        
        Args:
            plan_id: Unique identifier for the plan
            
        Returns:
            Plan metadata or None if not found
        """
        try:
            result = self.supabase.table(self.table_name).select("metadata, created_at, updated_at").eq("plan_id", plan_id).eq("is_active", True).execute()
            
            if result.data:
                plan_record = result.data[0]
                return {
                    "metadata": plan_record["metadata"],
                    "created_at": plan_record["created_at"],
                    "updated_at": plan_record["updated_at"]
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving metadata for plan '{plan_id}': {str(e)}")
            return None
