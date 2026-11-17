"""Workspace management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate,
    WorkspaceResponse, WorkspaceDetailResponse, WorkspaceMemberResponse,
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


def _role_to_str(role) -> str:
    """Helper to convert Enum or string role to a string."""
    return role.value if hasattr(role, "value") else str(role)


def _check_workspace_access(db: Session, workspace_id: str, user_id: str) -> WorkspaceMember:
    """Check if user has access to workspace and return membership."""
    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace",
        )
    return member


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new workspace (creator becomes owner)."""
    workspace = Workspace(name=payload.name, description=payload.description)
    db.add(workspace)
    db.flush()

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role=WorkspaceRole.OWNER,
    )
    db.add(member)
    db.commit()
    db.refresh(workspace)

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at,
        member_count=1,
        user_role=WorkspaceRole.OWNER.value,
    )


@router.get("/", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all workspaces the current user belongs to."""
    memberships = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.user_id == current_user.id)
        .all()
    )

    results = []
    for m in memberships:
        ws = m.workspace
        member_count = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == ws.id).count()
        results.append(WorkspaceResponse(
            id=ws.id,
            name=ws.name,
            description=ws.description,
            created_at=ws.created_at,
            member_count=member_count,
            user_role=_role_to_str(m.role),
        ))

    return results


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workspace details."""
    membership = _check_workspace_access(db, workspace_id, current_user.id)
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    members = []
    for m in workspace.members:
        members.append(WorkspaceMemberResponse(
            id=m.id,
            user_id=m.user_id,
            role=_role_to_str(m.role),
            user_email=m.user.email if m.user else "",
            user_name=m.user.full_name if m.user else "",
        ))

    return WorkspaceDetailResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at,
        member_count=len(members),
        user_role=_role_to_str(membership.role),
        members=members,
    )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: str,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update workspace details (owner/admin only)."""
    membership = _check_workspace_access(db, workspace_id, current_user.id)
    mem_role_str = _role_to_str(membership.role)
    if mem_role_str not in (WorkspaceRole.OWNER.value, WorkspaceRole.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can update workspace settings",
        )

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if payload.name is not None:
        workspace.name = payload.name
    if payload.description is not None:
        workspace.description = payload.description

    db.commit()
    db.refresh(workspace)
    member_count = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace.id).count()

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at,
        member_count=member_count,
        user_role=_role_to_str(membership.role),
    )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a workspace (owner only)."""
    membership = _check_workspace_access(db, workspace_id, current_user.id)
    if _role_to_str(membership.role) != WorkspaceRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete a workspace",
        )

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    db.delete(workspace)
    db.commit()
