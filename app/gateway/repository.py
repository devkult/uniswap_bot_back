from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, func
from dataclasses import dataclass
from entity.uniswap import Competition, CompetitionSwap, TopWalletHolder
from gateway.models import CompetitionModel, CompetitionSwapModel


@dataclass
class Repository:
    session: AsyncSession


@dataclass
class CompetitionRepository(Repository):

    async def add(self, competition: Competition) -> Competition:
        model = CompetitionModel(
            user_id=competition.user_id,
            competition_name=competition.name,
            token_address=competition.token_address,
            start_date=competition.start_date,
            end_date=competition.end_date,
            winner_wallet=competition.winner_wallet,
            channel_id=competition.channel_id,
        )
        self.session.add(model)
        await self.session.commit()
        competition.id = model.id
        return competition

    async def update(self, competition: Competition) -> Optional[Competition]:
        model = CompetitionModel(
            id=competition.id,
            user_id=competition.user_id,
            competition_name=competition.name,
            token_address=competition.token_address,
            start_date=competition.start_date,
            end_date=competition.end_date,
            winner_wallet=competition.winner_wallet,
            channel_id=competition.channel_id,
            last_processed_timestamp=competition.last_processed_datetime,
        )
        await self.session.merge(model)
        await self.session.commit()

    async def get(self, id: int) -> Optional[Competition]:
        model = await self.session.get(CompetitionModel, id)
        if model is None:
            return None
        return Competition(
            id=model.id,
            user_id=model.user_id,
            channel_id=model.channel_id,
            name=model.competition_name,
            token_address=model.token_address,
            start_date=model.start_date,
            end_date=model.end_date,
            winner_wallet=model.winner_wallet,
            last_processed_datetime=model.last_processed_timestamp,
        )

    async def get_all_active(self) -> list[Competition]:
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        models = await self.session.execute(
            select(CompetitionModel).where(
                and_(
                    CompetitionModel.end_date > current_time,
                    CompetitionModel.is_completed == False,
                )
            )
        )
        return [
            Competition(
                id=model.id,
                user_id=model.user_id,
                channel_id=model.channel_id,
                name=model.competition_name,
                token_address=model.token_address,
                start_date=model.start_date,
                end_date=model.end_date,
                winner_wallet=model.winner_wallet,
                last_processed_datetime=model.last_processed_timestamp,
            )
            for model in models.scalars().all()
        ]

    async def get_all_expired(self) -> list[Competition]:
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        result = await self.session.execute(
            select(CompetitionModel).where(
                and_(
                    CompetitionModel.end_date < current_time,
                    CompetitionModel.is_completed == False,
                )
            )
        )
        return [
            Competition(
                id=model.id,
                user_id=model.user_id,
                channel_id=model.channel_id,
                name=model.competition_name,
                token_address=model.token_address,
                start_date=model.start_date,
                end_date=model.end_date,
                winner_wallet=model.winner_wallet,
                last_processed_datetime=model.last_processed_timestamp,
            )
            for model in result.scalars().all()
        ]

    async def mark_as_completed(self, id: int, winner_address: str) -> None:
        model = await self.session.get(CompetitionModel, id)
        model.is_completed = True
        model.winner_wallet = winner_address
        await self.session.commit()


@dataclass
class CompetitionSwapRepository(Repository):

    async def bulk_insert(
        self, competition_swaps: list[CompetitionSwap]
    ) -> list[CompetitionSwap]:
        """
        Insert a list of CompetitionSwap objects into the database.
        """
        models = [
            CompetitionSwapModel(
                competition_id=competition_swap.competition_id,
                wallet_address=competition_swap.swap.sender,
                token_amount=competition_swap.swap.amount0,
                weth_amount=competition_swap.swap.amount1,
                timestamp=competition_swap.swap.datetime,
                pair=competition_swap.swap.pair,
            )
            for competition_swap in competition_swaps
        ]
        for model in models:
            self.session.add(model)

        await self.session.flush()
        await self.session.commit()

        for model, swap in zip(models, competition_swaps):
            swap.id = model.id
        return competition_swaps

    async def get_top_wallet_holder(
        self, competition_id: int
    ) -> Optional[TopWalletHolder]:
        result = await self.session.execute(
            select(
                CompetitionSwapModel.wallet_address,
                func.sum(CompetitionSwapModel.token_amount).label("total_amount"),
                CompetitionSwapModel.pair,
            )
            .where(CompetitionSwapModel.competition_id == competition_id)
            .group_by(CompetitionSwapModel.wallet_address, CompetitionSwapModel.pair)
            .order_by(func.sum(CompetitionSwapModel.token_amount).desc())
            .limit(1)
        )

        top_wallet = result.first()

        if not top_wallet:
            return None

        return TopWalletHolder(
            competition_id=competition_id,
            wallet_address=top_wallet.wallet_address,
            total_amount=top_wallet.total_amount,
            pair=top_wallet.pair,
        )
