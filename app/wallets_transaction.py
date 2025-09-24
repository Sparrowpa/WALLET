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
        operation_type: OperationType
) -> Decimal:
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма операции должна быть больше нуля")
    if amount > Decimal("99999999.99"):
        raise HTTPException(status_code=400, detail="Максимальная сумма: 99999999.99")

    async with session.begin():
        # Блокировка кошелька и получение
        wallet = await session.get(Wallet, wallet_id, with_for_update=True)
        if not wallet:
            raise HTTPException(status_code=404, detail="Кошелек не найден")

        # Обработка операций
        if operation_type == OperationType.DEPOSIT:
            if wallet.balance + amount > Decimal("99999999.99"):
                raise HTTPException(status_code=400, detail="Превышен максимальный баланс")
            wallet.balance += amount

        elif operation_type == OperationType.WITHDRAW:
            if wallet.balance < amount:
                raise HTTPException(status_code=400, detail="Недостаточно средств")
            wallet.balance -= amount

        else:
            raise HTTPException(status_code=400, detail="Неверный тип операции")

    await session.commit()
    return wallet.balance
