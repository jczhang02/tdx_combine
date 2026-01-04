import asyncio
from typing import Dict, List

from sqlalchemy import (
    URL,
    distinct,
    func,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import Session

from src.core.database.models import Base, Block, Stock, stock_block_association
from src.utils.types import Status


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


async def get_status(
    async_session: async_sessionmaker[AsyncSession],
) -> Status:
    ret: Status = {
        "status": 0,
        "block_count": 0,
        "stock_count": 0,
        "block_valid_count": 0,
        "update_at": None,
        "calc": 0,
    }
    try:
        async with async_session() as session:
            stmt_block = select(func.count()).select_from(Block)
            stmt_stock = select(func.count()).select_from(Stock)
            stmt_block_valid = select(
                func.count(distinct(stock_block_association.c.block_id))
            ).select_from(stock_block_association)
            block_count = await session.scalar(stmt_block)
            stock_count = await session.scalar(stmt_stock)
            block_valid_count = await session.scalar(stmt_block_valid)

            if block_count and stock_count:
                ret["status"] = 1
            ret["block_count"] = block_count
            ret["stock_count"] = stock_count
            ret["block_valid_count"] = block_valid_count

            stmt_update_at = select(func.max(Stock.updated_at))
            update_at = await session.scalar(stmt_update_at)
            ret["update_at"] = update_at

        return ret

    except Exception:
        return {
            "status": 0,
            "block_count": 0,
            "stock_count": 0,
            "update_at": None,
            "block_valid_count": 0,
            "calc": 0,
        }
