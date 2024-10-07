from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(kw_only=True)
class Pool:
    id: str
    token0: str
    token1: str


@dataclass(kw_only=True)
class Swap:
    id: str
    sender: str
    pair: str
    amount0: float
    amount1: float
    timestamp: int

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.timestamp, timezone.utc).replace(tzinfo=None)


@dataclass(kw_only=True)
class Competition:
    id: Optional[int] = None
    user_id: int
    name: str
    token_address: str
    start_date: datetime
    end_date: datetime
    winner_wallet: Optional[str] = None
    channel_id: int
    last_processed_datetime: Optional[datetime] = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    winner_prize: Optional[float] = None
    is_completed: bool = False

    @property
    def timestamp(self):
        return datetime.timestamp(self.last_processed_datetime)

    def update_datetime(self):
        self.last_processed_datetime = datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass(kw_only=True)
class CompetitionSwap:
    id: Optional[int] = None
    competition_id: str
    swap: Swap

    @classmethod
    def from_swap(cls, competition_id, swap: Swap):
        return cls(competition_id=competition_id, swap=swap)

@dataclass
class TopWalletHolder:
    competition_id: int
    wallet_address: str
    total_amount: float
    pair: str