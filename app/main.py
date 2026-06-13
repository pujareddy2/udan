from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import init_db

def create_app() -> FastAPI:
    # Initialize Database
    init_db()
    
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
        dashboard, ai_discovery, coach, intelligence, profile_context, search,
        voice_agent, timeline, approval
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
    app.include_router(voice_agent.router, prefix="/api/v1")
    app.include_router(timeline.router, prefix="/api/v1")
    app.include_router(approval.router, prefix="/api/v1")
    
    # Include Test Integrations router
    from app.api.routers import test_integration, telegram, jobseeker
    app.include_router(test_integration.router, prefix="/api/v1")
    app.include_router(telegram.router, prefix="/api/v1")
    app.include_router(jobseeker.router, prefix="/api/v1")

    # Serve the Live Voice UI Dashboard
    from fastapi.responses import HTMLResponse, JSONResponse
    import os
    
    @app.get("/", response_class=HTMLResponse, tags=["UI"])
    def get_main_ui():
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "UDAAN AI (standalone).html")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>UDAAN AI app not found.</h1>"

    @app.get("/voice", response_class=HTMLResponse, tags=["UI"])
    def get_voice_ui():
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voice_demo.html")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>Voice UI not found.</h1>"
        
    # Prevent confusing 404 logs in terminal for browser auto-requests
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return JSONResponse(content={})

    @app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
    def chrome_devtools():
        return JSONResponse(content={})

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "engines": 19}

    return app

app = create_app()
