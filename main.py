from fastapi import FastAPI
from app.wallets_router import wallets_router
from app.config import check_db_connection

app = FastAPI(title="Wallet API")
app.include_router(wallets_router, prefix="/api/v1")


app.add_event_handler("startup", check_db_connection)

# стартуем !!! uvicorn main:app --reload
