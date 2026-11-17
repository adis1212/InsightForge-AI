"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import InsightForgeException
from app.api.v1.router import router as api_v1_router
# Import models so Base.metadata is populated
from app.models.user import User  # noqa: F401
from app.models.workspace import Workspace, WorkspaceMember  # noqa: F401
from app.models.dataset import Dataset, DatasetColumn, KPIResult  # noqa: F401
from app.models.knowledge import KnowledgeDocument, DocumentChunk  # noqa: F401
from app.models.agent import AgentSession, AgentMessageRecord  # noqa: F401
from app.models.report import ReportRecord  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initialize database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Mobile-first B2B SaaS Augmented Analytics Platform",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler
    @app.exception_handler(InsightForgeException)
    async def insightforge_exception_handler(request: Request, exc: InsightForgeException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    # Health check
    @app.get("/api/v1/health", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    # Include API routes
    app.include_router(api_v1_router)

    return app


app = create_app()
