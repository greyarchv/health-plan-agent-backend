from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    age: int
    weight: float
    height: float
    fitness_goals: str
    fitness_goal_type: str
    injuries_limitations: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    fitness_goals: Optional[str] = None
    fitness_goal_type: Optional[str] = None
    injuries_limitations: Optional[str] = None

class User(UserBase):
    id: int
    supabase_user_id: Optional[str] = None
    email: Optional[str] = None
    email_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Workout Schemas
class WorkoutLogBase(BaseModel):
    exercise_name: str
    sets: int
    reps: int
    weight: float
    notes: Optional[str] = None

class WorkoutLogCreate(WorkoutLogBase):
    pass

class WorkoutLog(WorkoutLogBase):
    id: int
    user_id: int
    workout_date: datetime

    class Config:
        from_attributes = True

class WorkoutPlan(BaseModel):
    week_plan: List[Dict[str, Any]]
    exercises: List[Dict[str, Any]]

# Nutrition Schemas
class MealPlanBase(BaseModel):
    meal_type: str
    meal_data: Dict[str, Any]
    calories: int
    protein: float
    carbs: float
    fat: float

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    id: int
    user_id: int
    plan_date: datetime

    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessageBase(BaseModel):
    content: str
    role: str = "user"
    agent_type: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    user_id: int
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    detail: str 
# Authentication Schemas
class AuthRequest(BaseModel):
    email: str
    password: str

class AuthSignUpRequest(BaseModel):
    email: str
    password: str
    name: str
    age: int
    weight: float
    height: float
    fitness_goals: str
    fitness_goal_type: str
    injuries_limitations: Optional[str] = None

class OAuthRequest(BaseModel):
    provider: str  # "google" or "apple"
    access_token: str
    user_info: Optional[Dict[str, Any]] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
    expires_in: Optional[int] = None

class TokenVerificationRequest(BaseModel):
    token: str

class TokenVerificationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetResponse(BaseModel):
    success: bool
    message: str
