"""
Execution Service - Tool Registry
Concrete implementation of the tool registry.
"""

from typing import Dict
from ...interfaces.tool_port import ITool
from .gmail_tools import GmailAuthTool, GmailFetchTool
from .slack_tools import SlackPostTool
from .llm_tools import LLMSummarizeTool


class ToolRegistry:
    """
    Registry for managing and retrieving tools.
    
    This is the concrete implementation of IToolRegistry that maps
    tool names to their implementations.
    """
    
    def __init__(self):
        """Initialize the registry with available tools."""
        self._tools: Dict[str, ITool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register all default tools."""
        # Gmail tools
        self.register("gmail_auth", GmailAuthTool())
        self.register("gmail_fetch", GmailFetchTool())
        
        # Slack tools
        self.register("slack_post", SlackPostTool())
        
        # LLM tools
        self.register("llm_summarize", LLMSummarizeTool())
    
    def register(self, name: str, tool: ITool) -> None:
        """
        Register a tool with a given name.
        
        Args:
            name: Unique name for the tool
            tool: Tool instance implementing ITool protocol
        """
        self._tools[name] = tool
    
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
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry. Available tools: {list(self._tools.keys())}")
        return self._tools[name]
    
    def has(self, name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            name: Name of the tool to check
            
        Returns:
            True if tool is registered, False otherwise
        """
        return name in self._tools
    
    def list_tools(self) -> list[str]:
        """
        Get list of all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
