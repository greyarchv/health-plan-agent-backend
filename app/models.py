from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    supabase_user_id = Column(String, unique=True, nullable=True, index=True)  # For OAuth providers
    email = Column(String, unique=True, nullable=True, index=True)  # For email authentication
    email_verified = Column(Boolean, default=False)  # Email verification status
    
    # Profile fields (matching the actual database schema)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    height = Column(Float, nullable=False)  # in cm
    fitness_goals = Column(Text, nullable=False)  # JSON string of goals
    fitness_goal_type = Column(String, nullable=False)  # e.g., "building_muscle", "weight_loss", "strength", "endurance"
    injuries_limitations = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workout_logs = relationship("WorkoutLog", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")
    workout_plans = relationship("WorkoutPlan", back_populates="user")
    exercise_records = relationship("ExerciseRecord", back_populates="user")
    last_workouts = relationship("LastWorkout", back_populates="user")
    nutrition_checklists = relationship("NutritionChecklist", back_populates="user")

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    workout_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="workout_logs")

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_plan = Column(JSON, nullable=False)  # Array of WorkoutDay objects
    goal_type = Column(String, nullable=False)  # e.g., "building_muscle", "weight_loss", "strength"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workout_plans")

class ExerciseRecord(Base):
    __tablename__ = "exercise_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    max_weight = Column(Float, nullable=False, default=0.0)  # in kg
    max_sets = Column(Integer, nullable=False, default=3)
    max_reps = Column(Integer, nullable=False, default=10)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="exercise_records")

class LastWorkout(Base):
    __tablename__ = "last_workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_day = Column(String, nullable=False)  # e.g., "Day 1", "Day 2"
    workout_focus = Column(String, nullable=False)  # e.g., "Chest & Triceps"
    completed_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="last_workouts")

class CurrentWorkoutSession(Base):
    __tablename__ = "current_workout_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_day = Column(String, nullable=False)  # e.g., "Day 1", "Day 2"
    workout_focus = Column(String, nullable=False)  # e.g., "Chest & Triceps"
    current_exercise_index = Column(Integer, nullable=False, default=0)
    exercises = Column(JSON, nullable=False)  # Array of exercises for this day
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")

class WorkoutDay:
    """Data class for workout day structure"""
    def __init__(self, day: str, focus: str, exercises: list):
        self.day = day
        self.focus = focus
        self.exercises = exercises
    
    def to_dict(self):
        return {
            "day": self.day,
            "focus": self.focus,
            "exercises": self.exercises
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            day=data.get("day", ""),
            focus=data.get("focus", ""),
            exercises=data.get("exercises", [])
        )

class Exercise(Base):
    """Database model for exercises"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)  # push, pull, legs, core, other
    description = Column(Text, nullable=True)
    muscle_groups = Column(JSON, nullable=True)  # List of muscle groups
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ExerciseData:
    """Data class for exercise structure (for backward compatibility)"""
    def __init__(self, name: str, sets: int = 3, reps: int = 10, weight: float = 0.0):
        self.name = name
        self.sets = sets
        self.reps = reps
        self.weight = weight
    
    def to_dict(self):
        return {
            "name": self.name,
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name", ""),
            sets=data.get("sets", 3),
            reps=data.get("reps", 10),
            weight=data.get("weight", 0.0)
        )

class MealPlan(Base):
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_date = Column(DateTime(timezone=True), server_default=func.now())
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    meal_data = Column(JSON, nullable=False)  # Structured meal data
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    agent_type = Column(String, nullable=True)  # workout_creation, coach, accountability, meal_planning, nutrition_support
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages") 

class NutritionChecklist(Base):
    __tablename__ = "nutrition_checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checklist_date = Column(Date, nullable=False)
    completed_supplements = Column(Text)  # JSON string of completed supplements
    protein_progress = Column(Float, default=0.0)
    carbs_progress = Column(Float, default=0.0)
    fat_progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="nutrition_checklists") 