from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, field_validator

from entity.uniswap import Competition, TopWalletHolder


class CreateCompetitionRequestSchema(BaseModel):
    competition_name: str
    token_address: str
    start_date: datetime
    end_date: datetime
    channel_id: int
    user_id: int

    @field_validator("start_date", "end_date", mode="after")
    def validate_naive_datetime(cls, v: datetime):
        if v.tzinfo is not None:
            raise ValueError("Datetime must be offset-naive (without timezone)")
        return v


class CreateCompetitionResponseSchema(BaseModel):
    competition_id: int



class GetCompetitionResponseSchema(BaseModel):
    id: int
    name: str
    token_address: str
    start_date: datetime
    end_date: datetime
    winner_wallet: str
    channel_id: int
    last_processed_datetime: datetime
    is_completed: bool
    winner_prize: Optional[float]

    @classmethod
    def from_entity(cls, entity: Competition):
        return cls(
            id=entity.id,
            name=entity.name,
            token_address=entity.token_address,
            start_date=entity.start_date,
            end_date=entity.end_date,
            winner_wallet=entity.winner_wallet,
            channel_id=entity.channel_id,
            last_processed_datetime=entity.last_processed_datetime,
            is_completed=entity.is_completed,
            winner_prize=entity.winner_prize
        )

class DeleteCompetitionResponseSchema(BaseModel):
    id: int

    @classmethod
    def from_entity(cls, entity: Competition):
        return cls(id=entity.id)


class PatchCompetitionRequestSchema(BaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    winner_prize: Optional[float] = None

    @field_validator("start_date", "end_date", mode="after")
    def validate_naive_datetime(cls, v: datetime):
        if v.tzinfo is not None:
            raise ValueError("Datetime must be offset-naive (without timezone)")
        return v


class GetTopWalletHolderResponseSchema(BaseModel):
    wallet_address: str
    total_amount: float

    @classmethod
    def from_entity(
        cls, entity: Union[TopWalletHolder, list[TopWalletHolder]]
    ) -> Union["GetTopWalletHolderResponseSchema", list["GetTopWalletHolderResponseSchema"]]:
        if isinstance(entity, list):
            return [
                cls(wallet_address=e.wallet_address, total_amount=e.total_amount)
                for e in entity
            ]
        return cls(
            wallet_address=entity.wallet_address, total_amount=entity.total_amount
        )
