"""API v1 router aggregation."""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, workspaces, datasets, analytics, prompts, knowledge, agent, reports

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(workspaces.router)
router.include_router(datasets.router)
router.include_router(analytics.router)
router.include_router(prompts.router)
router.include_router(knowledge.router)
router.include_router(agent.router)
router.include_router(reports.router)
