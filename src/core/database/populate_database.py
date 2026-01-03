from typing import Dict, List, cast

from sqlalchemy import delete, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

import src.core.database.helpers as helpers
from src.core.database.models import (
    Block,
    CalcResult,
    Mode,
    Stock,
    stock_block_association,
)
from src.utils.types import CombinationResultDict


async def clear_database(
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    """clear tables [blocks, stocks, stock_block_association, mode]

    Parameters
        ----------
        async_session : async_sessionmaker[AsyncSession]
        Asyncio version of Session.

    """
    async with async_session() as session:
        await session.execute(delete(stock_block_association))
        await session.execute(delete(Stock))
        await session.execute(delete(Block))
        await session.execute(delete(Mode))
        await session.commit()


async def blocks2database(
    async_session: async_sessionmaker[AsyncSession],
    data: List[Dict[str, str]],
) -> None:
    """Insert blocks data into the database.

    Parameters
        ----------
        async_session : async_sessionmaker[AsyncSession]
            Asyncio version of Session.
        data : List[Dict[str, str]]
            List of block data to be inserted.

    """
    async with async_session() as session:
        stmt = insert(Block).values(data)
        await session.execute(stmt)
        await session.commit()


async def stocks2database(
    async_session: async_sessionmaker[AsyncSession],
    data: List[Dict[str, List[str] | str]],
) -> None:
    """Insert stocks data into the database and create stock-block associations.

    Parameters
        ----------
        async_session : async_sessionmaker[AsyncSession]
            Asyncio version of Session.
        data : List[Dict[str, List[str] | str]]
            List of stock data to be inserted, including block associations.

    """
    async with async_session() as session:
        block_codes = cast(
            Dict[str, List[str]],
            {item["code"]: item.pop("blocks") for item in data},
        )
        for item in data:
            item.pop("blocks", None)

        stmt = insert(Stock).values(data)

        await session.execute(stmt)
        await session.commit()

        blocks = await helpers.construct_blocks(
            async_session=async_session,
            block_codes=block_codes,
        )

        stmt = insert(stock_block_association).values(blocks)
        await session.execute(stmt)
        await session.commit()

        # print(Block.stocks.property.uselist)

        # b1 = await session.execute(select(Block).options(selectinload(Block.stocks)).where(Block.id == 99))
        # b2 = b1.scalar_one()


async def infoharbor2database(
    async_session: async_sessionmaker[AsyncSession],
    data: List[Dict[str, str | List[dict]]],
) -> None:
    """Insert additional infoharbor data and create stock-block associations.

    Parameters
        ----------
        async_session : async_sessionmaker[AsyncSession]
            Asyncio version of Session.
        data : List[Dict[str, str | List[dict]]]
            List of block data with associated stocks.

    """
    async with async_session() as session:
        for line in data:
            block_code: str = cast(str, line["code"])
            stmt_block_id = select(Block.id).where(Block.code == block_code)
            result = await session.execute(stmt_block_id)
            block_id: int = result.scalar_one()

            stocks: List[dict] = cast(List[dict], line["stocks"])
            stmt = (
                insert(Stock)
                .values(stocks)
                .on_conflict_do_nothing(index_elements=[Stock.code])
            )
            await session.execute(stmt)
            await session.flush()

            mapping: List[Dict[str, int]] = []

            for stock in stocks:
                stock_code: str = cast(str, stock["code"])

                stmt_stock_id = select(Stock.id).where(Stock.code == stock_code)
                result = await session.execute(stmt_stock_id)
                stock_id: int = result.scalar_one()

                mapping.append(
                    {
                        "stock_id": stock_id,
                        "block_id": block_id,
                    }
                )

            stmt = insert(stock_block_association).values(mapping)
            stmt = insert(stock_block_association).values(mapping)
            await session.execute(stmt)

        await session.commit()


async def insert_block2mode(
    async_session: async_sessionmaker[AsyncSession],
    value: str,
) -> None:
    """Function for inserting manual added block item to Mode.

    Parameters
    ----------
    async_session : async_sessionmaker[AsyncSession]
        Asyncio version of Session.
    value : str
        Block code from dropdown control.

    """
    async with async_session() as session:
        stmt = (
            select(Block)
            .options(selectinload(Block.stocks))
            .where(Block.code == value)
        )
        result = await session.execute(stmt)
        matching = result.scalar_one()
        values = {
            "code": matching.code,
            "name": matching.name,
            "count": len(matching.stocks),
        }
        await session.execute(
            insert(Mode)
            .values(values)
            .on_conflict_do_nothing(index_elements=[Mode.code])
        )
        await session.commit()


async def update_database(
    async_session: async_sessionmaker[AsyncSession],
    blocks: List[dict],
    stocks: List[dict],
    addition: List[dict],
    is_clear: bool = True,
) -> None:
    """Database function used to insert or update extracted data into sqlite database.

    Parameters
    ----------
    async_session : async_sessionmaker[AsyncSession]
        Asyncio version of Session.
    blocks : List[dict]
        Blocks information from 'get_blocks'.
    stocks : List[dict]
        Stocks information from 'get_stocks'
    addition : List[dict]
        Addition information from 'get_addition'
    is_clear : bool
        Whether to clear database before the function is execute.

    """
    # TODO: insert and update

    if is_clear:
        await clear_database(async_session=async_session)

        await blocks2database(
            async_session=async_session,
            data=blocks,
        )
        await stocks2database(
            async_session=async_session,
            data=stocks,
        )
        await infoharbor2database(
            async_session=async_session,
            data=addition,
        )


async def mode2database(
    async_session: async_sessionmaker[AsyncSession],
    blocks: List[str],
) -> None:
    """Create mode records from block data and save to database.

    Parameters
        ----------
        session : Session
            SQLAlchemy session.
        matching : List[str]
            List of Block code to convert to Mode records.

    """
    async with async_session() as session:
        await session.execute(delete(Mode))
        await session.commit()

    async with async_session() as session:
        stmt = (
            select(Block)
            .options(selectinload(Block.stocks))
            .where(Block.code.in_(blocks))
        )
        result = await session.execute(stmt)
        matching = result.all()

        data = []
        for (record,) in matching:
            mode = {
                "code": record.code,
                "name": record.name,
                "count": len(record.stocks),
            }
            data.append(mode)

        stmt = insert(Mode).values(data)
        await session.execute(stmt)
        await session.commit()


async def result2database(
    async_session: async_sessionmaker[AsyncSession],
    result: List[CombinationResultDict],
) -> None:
    async with async_session() as session:
        await session.execute(delete(CalcResult))
        await session.commit()

    async with async_session() as session:
        await session.execute(insert(CalcResult).values(result))
        await session.commit()
