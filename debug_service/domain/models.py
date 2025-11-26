from pydantic import BaseModel
from typing import List, Optional, Literal


class DebugIssue(BaseModel):
    severity: Literal["info", "warning", "error"]
    description: str
    location: Optional[str] = None


class SuggestedFix(BaseModel):
    description: str


class DebugReport(BaseModel):
    request_id: str
    summary: str
    issues: List[DebugIssue] = []
    suggested_fixes: List[SuggestedFix] = []
