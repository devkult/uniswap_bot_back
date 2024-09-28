from datetime import datetime
from pydantic import BaseModel, field_validator


class CreateCompetitionRequestSchema(BaseModel):
    competition_name: str
    token_address: str
    start_date: datetime
    end_date: datetime
    channel_id: int
    user_id: int

    @field_validator('start_date', 'end_date', mode='after')
    def validate_naive_datetime(cls, v: datetime):
        if v.tzinfo is not None:
            raise ValueError("Datetime must be offset-naive (without timezone)")
        return v

class CreateCompetitionResponseSchema(BaseModel):
    competition_id: int

class GetTopWalletHolderResponseSchema(BaseModel):
    top_wallet_holder: str
    total_amount: float
    