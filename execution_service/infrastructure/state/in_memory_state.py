"""
Execution Service - In-Memory State
Simple in-memory implementation of execution state storage for V1.
"""

from typing import Any, Dict


class InMemoryExecutionState:
    """
    In-memory storage for execution state.
    
    This is a simple V1 implementation. For production, consider:
    - Redis for distributed state
    - Database for persistence
    - File system for debugging
    """
    
    def __init__(self):
        """Initialize empty state storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    async def save(self, request_id: str, state: Dict[str, Any]) -> None:
        """
        Save execution state.
        
        Args:
            request_id: Unique identifier for the execution request
            state: State data to persist
        """
        self._storage[request_id] = state.copy()
    
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
        if request_id not in self._storage:
            raise KeyError(f"No state found for request_id: {request_id}")
        return self._storage[request_id].copy()
    
    async def exists(self, request_id: str) -> bool:
        """
        Check if state exists for a request.
        
        Args:
            request_id: Unique identifier for the execution request
            
        Returns:
            True if state exists, False otherwise
        """
        return request_id in self._storage
    
    def clear(self) -> None:
        """Clear all stored state (useful for testing)."""
        self._storage.clear()
