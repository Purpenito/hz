from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSettingsORM(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled_exchanges_json: Mapped[str] = mapped_column(Text)
    enabled_arbitrage_types_json: Mapped[str] = mapped_column(Text)
    min_profit_pct: Mapped[float] = mapped_column(Float, default=0.1)
    min_volume_24h: Mapped[float] = mapped_column(Float, default=100000)
    capital_usdt: Mapped[float] = mapped_column(Float, default=100)
    min_executable_ratio_pct: Mapped[float] = mapped_column(Float, default=50)
    max_signal_age_ms: Mapped[int] = mapped_column(Integer, default=10000)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SentSignalORM(Base):
    __tablename__ = "sent_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    signal_key: Mapped[str] = mapped_column(String(255), index=True)
    symbol: Mapped[str] = mapped_column(String(64))
    arbitrage_type: Mapped[str] = mapped_column(String(64))
    long_exchange: Mapped[str] = mapped_column(String(32))
    short_exchange: Mapped[str] = mapped_column(String(32))
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
