from datetime import datetime
from typing import Union
from pydantic import BaseModel, field_validator

from entity.uniswap import TopWalletHolder


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
