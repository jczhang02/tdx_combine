from typing import cast

import flet as ft
from omegaconf import DictConfig, OmegaConf
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.core import get_combination_count, update_data
from src.core.database import Base, mode2database
from src.core.database.helpers import get_status
from src.core.database.models import CalcResult, Mode
from src.core.readers.modes import get_modes
from src.ui import App
from src.utils.constants import CONFIG_PATH, DATABASE_URL


async def run():
    with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
        cfg: DictConfig = cast(DictConfig, OmegaConf.load(fp))
    # time1 = time.time()

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

    ret = await get_status(async_session=async_session)
    print(ret)

    re = await update_data(
        async_session=async_session,
        TDX_CACHE_DIR=cfg["TDX_CACHE_DIR"],
        BLOCK_PATH=cfg["BLOCK_PATH"],
        STOCK_PATH=cfg["STOCK_PATH"],
        ADDITIONAL_PATH=cfg["ADDITIONAL_PATH"],
        is_clear=True,
    )

    # time2 = time.time()

    # print(f"time for update data: {time2 - time1}")

    # print(re)

    blocks = await get_modes(path=cfg["MODE_PATH"])
    await mode2database(async_session=async_session, blocks=blocks)

    # time2 = time.time()
    ret = await get_combination_count(
        async_session=async_session,
    )

    print(ret)

    # export_combinations(
    #     path=cfg["RET_SAVE_DIR"],
    #     ret=ret,
    # )

    # block = session.query(Block).filter(Block.id == 99).one_or_none()
    # time3 = time.time()
    # print(time2 - time1)

    await engine.dispose()


async def main(page: ft.Page) -> None:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
        cfg: DictConfig = cast(DictConfig, OmegaConf.load(fp))

    engine: AsyncEngine = create_async_engine(
        url=cfg["DATABASE_URL"],
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

    async with async_session() as session:
        await session.execute(delete(Mode))
        await session.execute(delete(CalcResult))
        await session.commit()

    page.title = "TDX Combination"
    page.padding = 20
    app = App(async_session=async_session, cfg=cfg)
    page.add(app)

    await engine.dispose()


if __name__ == "__main__":
    ft.run(main)
    # asyncio.run(run())
