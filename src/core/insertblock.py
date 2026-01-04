import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database.models import Block
from src.core.database.populate_database import insert_block2database
from src.utils.types import Response


async def insert_block(
    async_session: async_sessionmaker[AsyncSession],
    block_code: str,
    path: str | os.PathLike[str],
) -> Response:
    try:
        async with async_session() as session:
            stmt = select(Block.id).where(Block.code == block_code)
            result_block_id = await session.execute(stmt)
            block_id = result_block_id.scalar_one_or_none()

            if not block_id:
                return Response(
                    code=601,
                    message=f"插入的板块 {block_code} 不存在",
                    data=None,
                )

            else:
                data = []
                with open(path, "r", encoding="gbk") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        else:
                            data.append(
                                {
                                    "code": line[1:],
                                    "region": line[0],
                                }
                            )

                await insert_block2database(
                    async_session=async_session,
                    block_id=block_id,
                    data=data,
                )

                return Response(
                    code=200,
                    message="SUCCESS",
                    data=None,
                )

    except Exception as e:
        return Response(
            code=600,
            message=f"插入板块数据时出现问题: {e}",
            data=None,
        )
