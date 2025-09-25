from fastapi import APIRouter, HTTPException
from decimal import Decimal
from uuid import UUID
from .wallets_transaction import create_wallet, process_transaction
from .models import OperationType, Wallet
from .config import async_session

wallets_router = APIRouter()


# Create a new wallet
@wallets_router.post("/wallets/new")
async def create_new_wallet():
    async with async_session() as session:
        wallet = await create_wallet(session)
        return {"wallet_id": str(wallet.id), "balance": wallet.balance}


# Get wallet balance
@wallets_router.get("/wallets/{wallet_id}")
async def get_balance(wallet_id: str):
    async with async_session() as session:
        try:
            wallet_uuid = UUID(wallet_id)
            wallet = await session.get(Wallet, wallet_uuid)
            if wallet is None:
                raise HTTPException(status_code=404, detail="Wallet not found")
            return {"wallet_id": wallet_id, "balance": wallet.balance}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid wallet ID format")
        except Exception as e:
            print(f"Error retrieving wallet: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Deposit / Withdraw
@wallets_router.post("/wallets/{wallet_id}/operation")
async def wallet_operation(
    wallet_id: str, operation_type: OperationType, amount: Decimal
):
    async with async_session() as session:
        new_balance = await process_transaction(
            session, wallet_id, amount, operation_type
        )

        return {
            "wallet_id": wallet_id,
            "new_balance": new_balance,  # Just return the new balance
        }
