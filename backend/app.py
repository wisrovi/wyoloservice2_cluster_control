"""Main FastAPI application for wyoloservice2_cluster_control."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import seed_default_admin
from backend.routers.auth_router import router as auth_router
from backend.routers.invokers_router import router as invokers_router
from backend.routers.overview_router import router as overview_router
from backend.routers.tasks_router import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: seeds admin user in Redis on startup."""
    print("=== [STARTUP] Starting Cluster Control Backend ===")
    seed_default_admin()
    yield
    print("=== [SHUTDOWN] Stopping Cluster Control Backend ===")


app = FastAPI(
    title="wyoloservice2_cluster_control API",
    description="Centralized Cluster Management and Dynamic Resource Allocation API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration to allow local Streamlit and remote dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(invokers_router)
app.include_router(tasks_router)
app.include_router(overview_router)


@app.get("/")
async def root():
    return {
        "service": "wyoloservice2_cluster_control",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
