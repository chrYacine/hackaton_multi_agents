"""
Execution Service - Gmail Tools
Mock implementations of Gmail-related tools for V1.
"""

from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class GmailAuthTool:
    """Mock tool for Gmail OAuth authentication."""
    
    async def run(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Gmail authentication.
        
        Args:
            context: Shared execution context
            parameters: Should contain credentials or auth config
            
        Returns:
            Dictionary with 'gmail_token' key
        """
        logger.info("🔐 GmailAuthTool: Simulating Gmail authentication...")
        
        # In real implementation, this would:
        # 1. Use OAuth2 credentials from parameters
        # 2. Authenticate with Gmail API
        # 3. Return access token
        
        # Mock response
        return {
            "gmail_token": "mock_gmail_token_abc123",
            "token_type": "Bearer",
            "expires_in": 3600,
            "authenticated": True
        }


class GmailFetchTool:
    """Mock tool for fetching emails from Gmail."""
    
    async def run(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate fetching emails from Gmail.
        
        Args:
            context: Should contain 'gmail_token' from previous auth step
            parameters: Should contain 'filter' (e.g., 'is:unread newer_than:30m')
            
        Returns:
            Dictionary with 'emails' key containing list of email objects
        """
        logger.info(f"📧 GmailFetchTool: Simulating email fetch with filter: {parameters.get('filter', 'none')}")
        
        # Verify token exists in context
        if "gmail_token" not in context:
            raise ValueError("Gmail token not found in context. Did gmail_auth run successfully?")
        
        # In real implementation, this would:
        # 1. Use token from context
        # 2. Apply filter from parameters
        # 3. Fetch emails via Gmail API
        # 4. Return structured email data
        
        # Mock response with sample emails
        mock_emails = [
            {
                "id": "email_001",
                "from": "alice@example.com",
                "subject": "Urgent: Project deadline",
                "snippet": "We need to discuss the project deadline for Q1...",
                "date": "2025-11-26T08:30:00Z",
                "labels": ["UNREAD", "IMPORTANT"]
            },
            {
                "id": "email_002",
                "from": "bob@company.com",
                "subject": "Meeting notes from yesterday",
                "snippet": "Here are the key points from our meeting...",
                "date": "2025-11-26T07:15:00Z",
                "labels": ["UNREAD"]
            },
            {
                "id": "email_003",
                "from": "notifications@github.com",
                "subject": "[repo] New pull request",
                "snippet": "A new pull request has been opened...",
                "date": "2025-11-26T06:45:00Z",
                "labels": ["UNREAD", "CATEGORY_UPDATES"]
            }
        ]
        
        return {
            "emails": mock_emails,
            "count": len(mock_emails),
            "filter_applied": parameters.get("filter", "none")
        }
