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

    # Note: Routers will be included here via an api_router
    # from app.api.v1.api import api_router
    # app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "engines": 19}

    return app

app = create_app()
