"""Agent API endpoints — Stage 8 Controlled Agentic AI Business Analyst."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.agent import AgentSession, AgentMessageRecord
from app.schemas.agent_schemas import (
    AgentChatRequest,
    AgentChatResponse,
    ConversationSessionSummary,
    AgentMessage,
    ToolExecutionTrace,
    EvidenceReference,
    ChartPayload,
)
from app.services.agent_service import agent_service

router = APIRouter(
    prefix="/workspaces/{workspace_id}/agent",
    tags=["AI Copilot Agent"],
)


def _check_workspace_access(db: Session, workspace_id: str, user: Optional[User]) -> None:
    """Verify workspace membership, permitting demo workspace access without token."""
    if workspace_id.startswith("demo-"):
        return
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for non-demo workspaces",
        )
    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")


@router.post("/chat", response_model=AgentChatResponse)
def copilot_chat(
    workspace_id: str,
    payload: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Chat with the Controlled LangGraph Business Analyst Agent.
    
    The agent dynamically classifies analytical intent and invokes only approved tools:
    - get_business_kpis
    - analyze_revenue_trends
    - get_product_performance
    - forecast_sales
    - detect_anomalies
    - retrieve_business_documents
    - generate_executive_report
    """
    _check_workspace_access(db, workspace_id, current_user)

    # Cloud LLM providers require authentication
    if payload.provider_type and payload.provider_type != "local_demo" and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to invoke cloud LLM providers.",
        )

    try:
        response = agent_service.execute_copilot(
            db=db,
            workspace_id=workspace_id,
            dataset_id=payload.dataset_id,
            user_message=payload.message,
            session_id=payload.session_id,
            provider_type=payload.provider_type or "local_demo",
        )
        return response
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err)) from val_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {exc}",
        ) from exc


@router.get("/sessions", response_model=list[ConversationSessionSummary])
def list_sessions(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """List recent conversation sessions for this workspace."""
    _check_workspace_access(db, workspace_id, current_user)
    sessions = (
        db.query(AgentSession)
        .filter(AgentSession.workspace_id == workspace_id)
        .order_by(AgentSession.updated_at.desc())
        .limit(20)
        .all()
    )
    return [
        ConversationSessionSummary(
            session_id=s.id,
            workspace_id=s.workspace_id,
            dataset_id=s.dataset_id,
            title=s.title,
            message_count=len(s.messages),
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=list[AgentMessage])
def get_session_messages(
    workspace_id: str,
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get all messages and execution traces for a conversation session."""
    _check_workspace_access(db, workspace_id, current_user)
    session = (
        db.query(AgentSession)
        .filter(AgentSession.id == session_id, AgentSession.workspace_id == workspace_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    messages_out = []
    for m in session.messages:
        traces = [
            ToolExecutionTrace(**t)
            for t in (m.execution_trace or [])
        ]
        evidences = [
            EvidenceReference(**e)
            for e in (m.evidence_references or [])
        ]
        chart = ChartPayload(**m.chart_payload) if m.chart_payload else None

        messages_out.append(
            AgentMessage(
                id=m.id,
                role=m.role,
                content=m.content,
                timestamp=m.created_at,
                intent=m.intent,
                tools_executed=m.tools_executed or [],
                execution_trace=traces,
                evidence_references=evidences,
                chart_payload=chart,
                structured_report=m.structured_report,
            )
        )
    return messages_out


@router.delete("/sessions/{session_id}")
def delete_session(
    workspace_id: str,
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Delete a conversation session and all its messages."""
    _check_workspace_access(db, workspace_id, current_user)
    session = (
        db.query(AgentSession)
        .filter(AgentSession.id == session_id, AgentSession.workspace_id == workspace_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"deleted": True, "session_id": session_id}
