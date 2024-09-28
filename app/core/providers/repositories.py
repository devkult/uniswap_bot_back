from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from gateway.repository import CompetitionRepository, CompetitionSwapRepository



class RepositoryProvider(Provider):
    scope = Scope.REQUEST


    @provide
    def get_competition_repository(self, session: AsyncSession) -> CompetitionRepository:
        return CompetitionRepository(session)

    @provide
    def get_competition_swap_repository(self, session: AsyncSession) -> CompetitionSwapRepository:
        return CompetitionSwapRepository(session)
    
