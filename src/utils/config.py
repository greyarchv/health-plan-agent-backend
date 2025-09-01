import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Configuration management for the health plan agent system."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Model Configuration
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    # System Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set")
        if not cls.ANTHROPIC_API_KEY:
            print("Warning: ANTHROPIC_API_KEY not set")
        return True

