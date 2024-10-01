import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Optional

from entity.uniswap import Competition, CompetitionSwap, TopWalletHolder
from gateway.repository import CompetitionRepository, CompetitionSwapRepository
from gateway.clients.uniswap_client import UniSwapAPIClient

logger = logging.getLogger("UniSwapBot")

@dataclass
class CompetitionService:
    uniswap_client: UniSwapAPIClient
    competition_repository: CompetitionRepository
    competition_swap_repository: CompetitionSwapRepository

    async def add_competition(self, competition: Competition) -> Competition:
        return await self.competition_repository.add(competition)
    
    async def get_competition(self, competition_id: int) -> Optional[Competition]:
        return await self.competition_repository.get(competition_id)
    
    async def get_competition_by_channel_id(self, channel_id: int) -> Optional[Competition]:
        return await self.competition_repository.get_by_channel_id(channel_id)
    
    
    async def get_all_competitions(self) -> list[Competition]:
        return await self.competition_repository.get_all_active()

    async def mark_competition_as_completed(self, competition_id: int, winner_address: str) -> None:
        await self.competition_repository.mark_as_completed(id=competition_id, winner_address=winner_address)
    
    async def get_all_competitions_that_expired(self) -> list[Competition]:
        return await self.competition_repository.get_all_expired()

    async def fetch_swaps(self, competition: Competition) -> list[CompetitionSwap]:
        swaps = await self.uniswap_client.fetch_swaps(
            token_address1=competition.token_address,
            token_address2="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            min_timestamp=competition.timestamp
        )

        competition_swaps = [
            CompetitionSwap.from_swap(competition_id=competition.id, swap=swap) for swap in swaps]

        await self.competition_swap_repository.bulk_insert(competition_swaps)

        competition.update_datetime()

        await self.competition_repository.update(competition)

        return competition_swaps

    async def get_top_wallet_holder(self, competition_id: int) -> Optional[TopWalletHolder]:
        return await self.competition_swap_repository.get_top_wallet_holders(competition_id=competition_id, top=1)
    
    async def get_top_wallet_holders(self, competition_id: int, top: int) -> list[TopWalletHolder]:
        return await self.competition_swap_repository.get_top_wallet_holders(competition_id=competition_id, top=top)