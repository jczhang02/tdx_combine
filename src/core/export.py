import os
from typing import List

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database import CalcResult
from src.utils.types import Response


async def export_combinations(
    path: str | os.PathLike[str],
    async_session: async_sessionmaker[AsyncSession],
) -> Response:
    NAME: List[str] = ["ZH1.blk", "ZH2.blk", "ZH3.blk"]

    try:
        async with async_session() as session:
            result = await session.execute(select(CalcResult))

        ret = []
        if result:
            ret = [calc_result for (calc_result,) in result.all()]

        if len(ret) != 3:
            return Response(
                code=500,
                message="组合计算结果个数错误",
                data=None,
            )

        for index, calc_result in enumerate(ret):
            save_name: str = os.path.join(path, NAME[index])

            blocks: List[str] = calc_result.blocks
            stocks: List[str] = calc_result.stocks

            async with aiofiles.open(save_name, "w") as f:
                for block in blocks:
                    await f.write(f"1{str(block)}" + "\n")

                for stock in stocks:
                    await f.write(str(stock) + "\n")

        return Response(
            code=200,
            message="SUCCESS",
            data=None,
        )

    except Exception as e:
        return Response(
            code=501,
            message=f"导出计算结果错误 {e}",
            data=None,
        )
