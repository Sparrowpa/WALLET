from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from .models import Wallet, OperationType, Transaction
from sqlalchemy.exc import OperationalError


async def create_wallet(session: AsyncSession) -> Wallet:
    wallet = Wallet()
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    return wallet


async def process_transaction(session, wallet_id: int, amount: Decimal, operation_type:OperationType ):

    try:
        async with session.begin():
            wallet = await session.get(
                Wallet,
                wallet_id,
                with_for_update=True,
            )
            if not wallet:
                raise HTTPException(status_code=404, detail="Wallet not found")

            if operation_type == OperationType.DEPOSIT:
                if wallet.balance + amount > Decimal("99999999.99"):
                    raise HTTPException(
                        status_code=400, detail="Maximum balance exceeded"
                    )
                wallet.balance += amount

            elif operation_type == OperationType.WITHDRAW:
                if wallet.balance < amount:
                    raise HTTPException(status_code=400, detail="Not enough funds")
                wallet.balance -= amount

            else:
                raise HTTPException(status_code=400, detail="Wrong operation type")

            transaction = Transaction(
                wallet_id=wallet.id,
                operation_type=operation_type.value,
                amount=amount,
            )
            session.add(transaction)

    except OperationalError:
        raise HTTPException(
            status_code=409, detail="Wallet is currently locked, try again later"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return wallet.balance
