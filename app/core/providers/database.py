from typing import AsyncIterable

from dishka import Provider, Scope, provide

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from redis.asyncio import Redis

from core.config import settings


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            f"{settings.db.url}",
            echo=False,
            pool_recycle=180,
        )

    @provide
    def get_session_maker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        session = factory()

        yield session

        await session.close()


    @provide(scope=Scope.APP)
    def get_redis_client(self) -> Redis:
        return Redis.from_url(settings.redis.url, decode_responses=True, socket_timeout=settings.redis.timeout)