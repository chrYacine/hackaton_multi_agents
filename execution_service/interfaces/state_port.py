"""
Execution Service - State Port
Defines the abstraction for execution state persistence (optional for V1).
"""

from typing import Any, Dict, Protocol


class IExecutionState(Protocol):
    """
    Protocol defining the interface for execution state persistence.
    
    This allows saving and loading execution state for resumability,
    debugging, or audit purposes.
    """
    
    async def save(self, request_id: str, state: Dict[str, Any]) -> None:
        """
        Save execution state.
        
        Args:
            request_id: Unique identifier for the execution request
            state: State data to persist
        """
        ...
    
    async def load(self, request_id: str) -> Dict[str, Any]:
        """
        Load execution state.
        
        Args:
            request_id: Unique identifier for the execution request
            
        Returns:
            Saved state data
            
        Raises:
            KeyError: If no state exists for the given request_id
        """
        ...
    
    async def exists(self, request_id: str) -> bool:
        """
        Check if state exists for a request.
        
        Args:
            request_id: Unique identifier for the execution request
            
        Returns:
            True if state exists, False otherwise
        """
        ...
