from contextlib import asynccontextmanager
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from core.ioc import get_container
from presentation.api.lifespan import fetch_updates_in_background, process_top_wallet_holders
from presentation.api.uniswap import router as api_router
from aiojobs import Scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan callback for FastAPI."""

    scheduler = Scheduler()
    update_job = await scheduler.spawn(fetch_updates_in_background())
    top_wallet_job = await scheduler.spawn(process_top_wallet_holders())

    try:
        yield
    finally:
        await update_job.close()
        await top_wallet_job.close()
        await app.state.dishka_container.close()


def create_app(container: AsyncContainer = get_container()) -> FastAPI:
    app = FastAPI(
        title="uniswap_bot_backend",
        description="Uniswap bot backend",
        docs_url="/api/docs",
        version="1.0.0",
        debug=True,
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix="/api")

    setup_dishka(container=container, app=app)

    return app
