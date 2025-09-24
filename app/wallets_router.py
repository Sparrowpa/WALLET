from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from .wallets_operation import create_wallet, get_wallet_balance, process_transaction
from .models import OperationType
from .config import async_session

wallets_router = APIRouter()


# Pydantic-схема для запроса транзакции
class OperationRequest(BaseModel):
    operation_type: str
    amount: Decimal


# Создание нового кошелька
@wallets_router.post("/wallets/new")
async def create_new_wallet():
    async with async_session() as session:
        wallet = await create_wallet(session)
        return {"wallet_id": str(wallet.id), "balance": wallet.balance}


# Получение баланса кошелька
@wallets_router.get("/wallets/{wallet_id}")
async def get_balance(wallet_id: str):
    async with async_session() as session:
        try:
            balance = await get_wallet_balance(session, wallet_id)
            return {"wallet_id": wallet_id, "balance": balance}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))


# депозит/снятие
@wallets_router.post("/wallets/{wallet_id}/operation")
async def wallet_operation(wallet_id: str, req: OperationRequest):
    async with async_session() as session:
        # Проверяем, что тип операции корректный
        try:
            op_type = OperationType(req.operation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный тип операции")

        # Проводим транзакцию через сервис
        try:
            # Возвращаем транзакцию и обновленный баланс
            transaction, balance = await process_transaction(session, wallet_id, req.amount, op_type)
            # Формируем ответ
            return {
                "transaction_id": str(transaction.id),
                "wallet_id": wallet_id,
                "amount": transaction.amount,
                "operation_type": transaction.operation_type,
                "balance": balance
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
