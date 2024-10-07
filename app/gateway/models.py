from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, BigInteger, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass



class CompetitionModel(Base):
    """Competition model."""

    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True)
    competition_name = Column(String)
    token_address = Column(String)
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime, server_default=func.now())

    winner_wallet = Column(String)
    channel_id = Column(BigInteger)

    last_processed_timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(BigInteger)
    is_completed = Column(Boolean, default=False)
    winner_prize = Column(Float, nullable=True)

    swaps = relationship("CompetitionSwapModel", cascade="all, delete", backref="competition")


class CompetitionSwapModel(Base):
    """Competition Swap model."""

    __tablename__ = "competition_swaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
    wallet_address = Column(String, nullable=False)
    token_amount = Column(Float, nullable=False)
    weth_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    pair = Column(String, nullable=False)


