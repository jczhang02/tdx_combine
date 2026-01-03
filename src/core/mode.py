from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database import Block, insert_block2mode, mode2database
from src.utils.types import Response


async def import_mode_list(
    async_session: async_sessionmaker[AsyncSession],
    blocks: List[str],
) -> Response:
    async with async_session() as session:
        stmt = select(Block).where(Block.code.in_(blocks))
        result = await session.execute(stmt)
        matching = result.all()

        if not matching:
            return {
                "code": 400,
                "message": "文件中无可用的板块代码",
                "data": None,
            }

        if len(matching) <= 3:
            return {
                "code": 401,
                "message": f"文件中仅有 {len(matching)} 可用代码",
                "data": None,
            }

        await mode2database(async_session=async_session, blocks=blocks)

        found_codes = [str(block.code) for (block,) in matching]
        not_found_codes = list(set(blocks) - set(found_codes))

        return {
            "code": 200,
            "message": "SUCCESS",
            "data": {
                "found_codes": list(found_codes),
                "not_found_codes": list(not_found_codes),
            },
        }


async def insert_mode_item(
    async_session: async_sessionmaker[AsyncSession],
    value: str,
) -> Response:
    try:
        await insert_block2mode(
            async_session=async_session,
            value=value,
        )
        return Response(
            code=200,
            message="SUCCESS",
            data=None,
        )
    except Exception as e:
        return Response(
            code=402,
            message=f"插入数据: 插入数据 {value} 时发生错误 {e}",
            data=None,
        )
