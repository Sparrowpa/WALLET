from fastapi import FastAPI
from app.wallets_router import wallets_router
from app.config import check_db_connection

app = FastAPI(title="Wallet API")
app.include_router(wallets_router, prefix="/api/v1")


async def startup_event():
    await check_db_connection()
app.add_event_handler("startup", startup_event)

# стартуем !!! uvicorn main:app --reload
