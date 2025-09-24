from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from .models import Wallet, Transaction, OperationType


# Функция для создания нового кошелька
async def create_wallet(session: AsyncSession) -> Wallet:

    wallet = Wallet()
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    return wallet

# Функция получения баланса кошелька
async def get_wallet_balance(session: AsyncSession, wallet_id: str) -> Decimal:

    try:
        wallet_uuid = UUID(wallet_id)  # конвертируем строку в UUID
    except ValueError:
        raise ValueError("Некорректный формат UUID")

    # __eq__ !!!!!разобрать
    stmt = select(Wallet).where(Wallet.id.__eq__(wallet_uuid))
    result = await session.execute(stmt)
    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise ValueError("Кошелек не найден")

    return wallet.balance

# Функция для проведения транзакции
async def process_transaction(
    session: AsyncSession,
    wallet_id: str,
    amount: Decimal,
    operation_type: OperationType
) -> tuple[Transaction, Decimal]:

    if amount <= 0:
        raise ValueError("Сумма операции должна быть больше нуля")

    if amount > Decimal("99999999.99"):
        raise ValueError("За эти деньги, ты можешь купить наш банк!Максимум:99999999.99")

    # Проверяем корректность UUID
    try:
        wallet_uuid = UUID(wallet_id)
    except ValueError:
        raise ValueError("Некорректный формат UUID")

    # Получаем кошелек с блокировкой
    stmt = select(Wallet).where(Wallet.id.__eq__(wallet_uuid)).with_for_update()
    result = await session.execute(stmt)
    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise ValueError("Кошелек не найден")

    # Проверяем корректность типа операции
    if operation_type not in [OperationType.DEPOSIT, OperationType.WITHDRAW]:
        raise ValueError("Неверный тип операции")

    if operation_type == OperationType.DEPOSIT:
        if wallet.balance + amount > Decimal("99999999.99"):
            raise ValueError(f"У тебя итак много денег,успокойся. Максимум:99999999.99")
        wallet.balance += amount

    # Логика операций
    if operation_type == OperationType.DEPOSIT:
        wallet.balance += amount
    elif operation_type == OperationType.WITHDRAW:
        if wallet.balance < amount:
            raise ValueError("Недостаточно средств для снятия")
        wallet.balance -= amount

    # Создаем транзакцию
    transaction = Transaction(
        wallet_id=wallet.id,
        amount=amount,
        operation_type=operation_type.value
    )
    session.add(transaction)

    try:
        await session.commit()
        await session.refresh(transaction)
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(f"Ошибка транзакции: {e}")

    # Возвращаем транзакцию и актуальный баланс кошелька
    return transaction, wallet.balance

