from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="Udaan AI - 19 Engine Microservice Architecture"
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include basic routers
    from app.api.routers import auth, profile, opportunities, wallet, lifecycle
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(profile.router, prefix="/api/v1")
    app.include_router(opportunities.router, prefix="/api/v1")
    app.include_router(wallet.router, prefix="/api/v1")
    app.include_router(lifecycle.router, prefix="/api/v1")
    
    # Include AI and Intelligence routers
    from app.api.routers import (
        eligibility, readiness, value, documents, notifications,
        dashboard, ai_discovery, coach, intelligence, profile_context, search
    )
    app.include_router(eligibility.router, prefix="/api/v1")
    app.include_router(readiness.router, prefix="/api/v1")
    app.include_router(value.router, prefix="/api/v1")
    app.include_router(documents.router, prefix="/api/v1")
    app.include_router(notifications.router, prefix="/api/v1")
    app.include_router(dashboard.router, prefix="/api/v1")
    app.include_router(ai_discovery.router, prefix="/api/v1")
    app.include_router(coach.router, prefix="/api/v1")
    app.include_router(intelligence.router, prefix="/api/v1")
    app.include_router(profile_context.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    
    # Include Test Integrations router
    from app.api.routers import test_integration
    app.include_router(test_integration.router, prefix="/api/v1")

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "engines": 19}

    return app

app = create_app()
