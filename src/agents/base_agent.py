from abc import ABC, abstractmethod
from typing import List, Dict, Any
import asyncio

class BaseAgent(ABC):
    """Base class for all agents in the health plan system."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools = []
    
    def add_tool(self, tool):
        """Add a tool to the agent's arsenal."""
        self.tools.append(tool)
    
    def get_tool(self, tool_name: str):
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]
    
    @abstractmethod
    async def process(self, **kwargs) -> Dict[str, Any]:
        """Process the agent's main task."""
        pass
    
    def get_description(self) -> str:
        """Get agent description."""
        return f"{self.name}: {self.description}"

