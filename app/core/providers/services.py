from dishka import Provider, Scope, provide

from gateway.repository import CompetitionRepository, CompetitionSwapRepository
from gateway.clients.uniswap_client import UniSwapAPIClient
from service.competition_service import CompetitionService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_competition_service(
        self,
        competition_repo: CompetitionRepository,
        competition_swap_repo: CompetitionSwapRepository,
        uni_swap_client: UniSwapAPIClient,
    ) -> CompetitionService:
        return CompetitionService(
            uniswap_client=uni_swap_client,
            competition_repository=competition_repo,
            competition_swap_repository=competition_swap_repo,
        )
