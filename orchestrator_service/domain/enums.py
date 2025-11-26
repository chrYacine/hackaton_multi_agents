"""
Orchestrator Service - Domain Enums
"""

from enum import Enum


class AgentType(str, Enum):
    """Supported agent types"""
    EMAIL_SUMMARY = "EMAIL_SUMMARY_AGENT"
    SLACK_ROUTER = "SLACK_ROUTER_AGENT"
    GITHUB_WATCHER = "GITHUB_WATCHER_AGENT"
    GENERIC = "GENERIC_AGENT"


class ApprovalStatus(str, Enum):
    """Status of plan approval"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
