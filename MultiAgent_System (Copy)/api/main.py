from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1) Load .env thật sớm
try:
    from dotenv import load_dotenv
    load_dotenv()  # đảm bảo .env có hiệu lực cho mọi import phía dưới
except Exception:
    pass

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.core.middleware import auth_middleware
# from api.src.keywords.routes import router as keywords_router
# from api.src.projects.routes import router as projects_router
from api.utils.migrations import run_migrations
# Thêm import
from api.src.MultiAgent.test_routes import router as test_router

# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
run_migrations()

# Set up logger for this module
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# ADd Config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add middleware
app.middleware("http")(auth_middleware)

# Include routers
# app.include_router(prefix="/api/v1/projects", router=projects_router)
# app.include_router(prefix="/api/v1/keywords", router=keywords_router)
# Thêm router (sau các router hiện có)
app.include_router(test_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": "Welcome to Keyword API!"}
