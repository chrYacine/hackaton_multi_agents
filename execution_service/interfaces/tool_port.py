"""
Execution Service - Tool Port
Defines the abstraction for tools that can be executed.
"""

from typing import Any, Dict, Protocol


class ITool(Protocol):
    """
    Protocol defining the interface for executable tools.
    
    Tools are the building blocks of execution plans. Each tool performs
    a specific action (e.g., authenticate with Gmail, fetch emails, post to Slack).
    """
    
    async def run(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given context and parameters.
        
        Args:
            context: Shared execution context (state accumulated from previous steps)
            parameters: Tool-specific parameters from the execution step
            
        Returns:
            Dictionary containing the tool's output, which will be merged into context
            
        Raises:
            Exception: If tool execution fails
        """
        ...


class IToolRegistry(Protocol):
    """
    Protocol defining the interface for tool registration and retrieval.
    """
    
    def register(self, name: str, tool: ITool) -> None:
        """
        Register a tool with a given name.
        
        Args:
            name: Unique name for the tool (e.g., 'gmail_auth', 'slack_post')
            tool: Tool instance implementing ITool protocol
        """
        ...
    
    def get(self, name: str) -> ITool:
        """
        Retrieve a tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            Tool instance
            
        Raises:
            KeyError: If tool is not registered
        """
        ...
    
    def has(self, name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            name: Name of the tool to check
            
        Returns:
            True if tool is registered, False otherwise
        """
        ...
