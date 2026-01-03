import asyncio
from typing import Dict, List

from sqlalchemy import (
    URL,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import Session

from .models import Base, Block, Stock


async def create_async_session(
    DATABASE_URL: str | URL,
) -> async_sessionmaker[AsyncSession]:
    engine: AsyncEngine = create_async_engine(
        url=DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        echo=False,
    )
    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return async_session


def get_block_list(session: Session) -> list:
    blocks_code: List[Dict[str, str]] = [
        {
            "code": v1,
            "name": v2,
        }
        for (v1, v2) in session.query(Block.code, Block.name).all()
    ]
    return blocks_code


async def construct_blocks(
    async_session: async_sessionmaker[AsyncSession],
    block_codes: Dict[str, List[str]],
) -> List[Dict[str, str]]:
    unique_stock_codes = list(block_codes.keys())
    unique_block_codes = set()
    for blocks in block_codes.values():
        unique_block_codes.update(blocks)
    unique_block_codes = list(unique_block_codes)

    async def get_stock_id(stock_code):
        async with async_session() as session:
            stmt = select(Stock.id).where(Stock.code == stock_code)
            result = await session.execute(stmt)
            return stock_code, result.scalar_one()

    async def get_block_id(block_code):
        async with async_session() as session:
            stmt = select(Block.id).where(Block.code == block_code)
            result = await session.execute(stmt)
            return block_code, result.scalar_one()

    stock_tasks = [get_stock_id(code) for code in unique_stock_codes]
    block_tasks = [get_block_id(code) for code in unique_block_codes]

    stock_results, block_results = await asyncio.gather(
        asyncio.gather(*stock_tasks),
        asyncio.gather(*block_tasks),
    )

    stock_id_map = dict(stock_results)
    block_id_map = dict(block_results)

    blocks = []
    for stock_code, block_code_list in block_codes.items():
        stock_id = stock_id_map[stock_code]
        for block_code in block_code_list:
            block_id = block_id_map[block_code]
            blocks.append({"stock_id": stock_id, "block_id": block_id})

    return blocks
