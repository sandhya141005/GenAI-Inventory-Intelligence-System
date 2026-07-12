from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import public
from app.api.routers import analytics, auth, copilot, donations, health, realm
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description="Backend decision intelligence layer for inventory analytics.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix=settings.API_PREFIX)
    app.include_router(auth.router, prefix=settings.API_PREFIX)
    app.include_router(copilot.router, prefix=settings.API_PREFIX)
    app.include_router(analytics.router, prefix=settings.API_PREFIX)
    app.include_router(donations.router, prefix=settings.API_PREFIX)
    app.include_router(realm.router, prefix=settings.API_PREFIX)
    app.include_router(public.router, prefix=settings.API_PREFIX)
    return app


app = create_app()
