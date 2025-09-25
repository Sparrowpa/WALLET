import pytest_asyncio
import pytest
import asyncio
import httpx
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/wallet_db"

# async engine
engine = create_async_engine(DATABASE_URL, future=True, echo=False)

# async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as ac:
        yield ac


@pytest_asyncio.fixture
async def db():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_concurrent_wallet_operations(client, db):
    # create a new wallet
    create_res = await client.post("/api/v1/wallets/new")
    assert create_res.status_code == 200
    wallet_id = create_res.json()["wallet_id"]

    # reset the balance explicitly
    await db.execute(text(f"UPDATE wallets SET balance = 0 WHERE id = '{wallet_id}'"))
    await db.commit()

    # prepare operations
    operations = []
    for _ in range(5):
        operations.append({"operation": "DEPOSIT", "amount": 100})  # ❌here we set test
        operations.append({"operation": "WITHDRAW", "amount": 50})  # ❌here we set test

    async def send_request(op):
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            params={"operation_type": op["operation"], "amount": op["amount"]},
        )

    results = await asyncio.gather(*[send_request(op) for op in operations])

    for res in results:
        assert res.status_code == 200, res.text

    # check the final balance
    result = await db.execute(
        text(f"SELECT balance FROM wallets WHERE id = '{wallet_id}'")
    )
    final_balance = result.scalar_one()

    assert final_balance == Decimal("250.00")
