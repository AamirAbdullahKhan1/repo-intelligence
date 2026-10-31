"""Local API: queued intake, saved snapshots and bounded graph projections."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Settings, get_settings
from app.jobs import Jobs
from app.persistence.store import Store
from app.api.routes import register_routes


def create_app(settings: Settings | None = None):
    settings = settings or get_settings()
    data = settings.data_dir.resolve()

    @asynccontextmanager
    async def lifespan(app):
        data.mkdir(parents=True, exist_ok=True)
        app.state.store = Store(data / 'analysis.sqlite')
        app.state.store.recover()
        app.state.jobs = Jobs(app.state.store, data)
        try:
            yield
        finally:
            app.state.jobs.shutdown()

    app = FastAPI(title='Repo Intelligence', version='1.0.0', lifespan=lifespan,
                  description='Deterministic local TypeScript/JavaScript repository analysis')
    app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins.split(','),
                       allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

    register_routes(app, data)

    return app


app = create_app()
