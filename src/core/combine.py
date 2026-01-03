from itertools import combinations
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database import (
    Block,
    Mode,
    Stock,
    result2database,
    stock_block_association,
)
from src.utils.types import CombinationResultDict, Response


async def get_combination_count(
    async_session: async_sessionmaker[AsyncSession],
    top_n: int = 3,
) -> Response:
    """Get count of combinations for a given path.

    Args:
        async_session: Database session factory
        top_n: Number of top combinations to return (default: 3)

    Returns:
        Response object containing combination count data
    """

    try:
        async with async_session() as session:
            stmt = select(Mode.code)
            result = await session.execute(stmt)
            blocks: List[str] = [code for (code,) in result.all()]

    except Exception as e:
        return Response(
            code=400,
            message=f"计算: 从数据库中读取列表错误 {e}",
            data=None,
        )

    try:
        block_tuple = list(combinations(blocks, 3))

        if len(block_tuple) <= 3:
            return Response(
                code=401,
                message="需计算的板块数量较少，请添加板块",
                data=None,
            )

        async with async_session() as session:
            block_info_stmt = select(Block.id, Block.code).where(
                Block.code.in_(blocks)
            )
            block_info_result = await session.execute(block_info_stmt)
            block_info_query = block_info_result.all()

        code2id_mapping = {code: id for id, code in block_info_query}

        results: dict = {}

        async with async_session() as session:
            for code_triplet in block_tuple:
                id_triplet = [code2id_mapping[code] for code in code_triplet]
                stmt = (
                    select(stock_block_association.c.stock_id)
                    .filter(stock_block_association.c.block_id.in_(id_triplet))
                    .group_by(stock_block_association.c.stock_id)
                    .having(func.count(stock_block_association.c.block_id) == 3)
                )
                result = await session.execute(stmt)
                common_stock_count = len(result.fetchall())
                results[code_triplet] = common_stock_count

        combination: List[tuple] = sorted(
            results.items(), key=lambda item: item[1], reverse=True
        )

        ret: List[CombinationResultDict] = []

        async with async_session() as session:
            for code_triplet, count in combination[:top_n]:
                id_triplet = [code2id_mapping[code] for code in code_triplet]
                stmt_common = (
                    select(stock_block_association.c.stock_id)
                    .filter(stock_block_association.c.block_id.in_(id_triplet))
                    .group_by(stock_block_association.c.stock_id)
                    .having(func.count(stock_block_association.c.block_id) == 3)
                )
                result = await session.execute(stmt_common)

                common_stock_ids = [row[0] for row in result.all()]

                stock_info_stmt = select(Stock.region, Stock.code).where(
                    Stock.id.in_(common_stock_ids)
                )

                stock_info_result = await session.execute(stock_info_stmt)

                common_stock_codes_with_region: List[str] = sorted(
                    [
                        f"{region}{code}"
                        for region, code in stock_info_result.all()
                    ]
                )

                ret.append(
                    {
                        "blocks": list(code_triplet),
                        "count": count,
                        "stocks": common_stock_codes_with_region,
                    }
                )

        await result2database(
            async_session=async_session,
            result=ret,
        )

        return Response(
            code=200,
            message="SUCCESS",
            data=None,
        )

    except Exception as e:
        return Response(
            code=401,
            message=f"计算组合: 计算过程中出现错误 {e}",
            data=None,
        )
