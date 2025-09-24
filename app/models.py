from sqlalchemy import Column, String, Numeric, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

Base = declarative_base()


class OperationType(enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


# wallets
class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance = Column(Numeric(10, 2), nullable=False, default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связь с транзакциями
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")

    # чтобы баланс не ушел в минус
    __table_args__ = (
        CheckConstraint('balance >= 0', name='non_negative_balance'),
    )


# transactions
class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)
    operation_type = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с кошельком
    wallet = relationship("Wallet", back_populates="transactions")

    # сумма должна быть положительной и тип операции корректный
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_amount'),
        CheckConstraint(
            "operation_type IN ('DEPOSIT', 'WITHDRAW')",
            name='valid_operation_type'
        ),
    )
