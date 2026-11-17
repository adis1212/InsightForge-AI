"""Pydantic schemas for workspaces."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkspaceCreate(BaseModel):
    """Create workspace request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    """Update workspace request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class WorkspaceMemberResponse(BaseModel):
    """Workspace member response."""
    id: str
    user_id: str
    role: str
    user_email: str = ""
    user_name: str = ""

    model_config = {"from_attributes": True}


class WorkspaceResponse(BaseModel):
    """Workspace response."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    member_count: int = 0
    user_role: str = ""

    model_config = {"from_attributes": True}


class WorkspaceDetailResponse(WorkspaceResponse):
    """Workspace detail response with members."""
    members: list[WorkspaceMemberResponse] = []
