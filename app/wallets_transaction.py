from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from .models import Wallet, OperationType


async def create_wallet(session: AsyncSession) -> Wallet:
    wallet = Wallet()
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    return wallet


async def process_transaction(
    session: AsyncSession,
    wallet_id: str,
    amount: Decimal,
    operation_type: OperationType,
) -> Decimal:
    if amount <= 0:
        raise HTTPException(
            status_code=400, detail="Transaction amount must be greater than zero"
        )
    if amount > Decimal("99999999.99"):
        raise HTTPException(status_code=400, detail="Maximum amount: 99999999.99")

    async with session.begin():
        # Lock the wallet
        wallet = await session.get(Wallet, wallet_id, with_for_update=True)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # Process the operations
        if operation_type == OperationType.DEPOSIT:
            if wallet.balance + amount > Decimal("99999999.99"):
                raise HTTPException(status_code=400, detail="Maximum balance exceeded")
            wallet.balance += amount

        elif operation_type == OperationType.WITHDRAW:
            if wallet.balance < amount:
                raise HTTPException(status_code=400, detail="Not enough funds")
            wallet.balance -= amount

        else:
            raise HTTPException(status_code=400, detail="Wrong operation type")

    await session.commit()  # SAVE!!!
    return wallet.balance
