from dishka import Provider, Scope, provide
from httpx import AsyncClient

from gateway.clients.uniswap_client import UniSwapAPIClient
from core.config import settings
from service.notifier import TelegramNotifier


class ClientProvider(Provider):
    scope = Scope.APP

    @provide
    def get_client_uniswap_api_client(self) -> UniSwapAPIClient:
        return UniSwapAPIClient(
            api_key=settings.uniswap.api_key,
            subgraph_id=settings.uniswap.subgraph_id,
            http_client=AsyncClient(),
        )

    @provide
    def get_telegram_notifier(self) -> TelegramNotifier:
        return TelegramNotifier(token_bot=settings.telegram_bot_token)