from abc import ABC, abstractmethod
from typing import Any, Dict, List
import asyncio

class BaseTool(ABC):
    """Base class for all tools in the health plan agent system."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def get_description(self) -> str:
        """Get tool description for agent use."""
        return f"{self.name}: {self.description}"
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tool parameters schema."""
        return {}

