from typing import Dict, List

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database.models import Mode


def get_re_code_relationship(blocks: pd.DataFrame) -> Dict[str, str] | dict:
    mappings: Dict[str, str] = blocks.set_index(["re_code"])["code"].to_dict()
    return mappings


async def get_mode_data(
    async_session: async_sessionmaker[AsyncSession],
) -> List[Dict[str, str | int]]:
    async with async_session() as session:
        result = await session.execute(select(Mode))
        records = result.all()

    data: List[Dict[str, str | int]] = []
    for (record,) in records:
        data.append(
            {
                "code": record.code,
                "name": record.name,
                "count": record.count,
            }
        )

    return data
