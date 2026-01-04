import os
from typing import cast

import flet as ft
from omegaconf import DictConfig, OmegaConf
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from pathlib import Path
from src.core.database import Base
from src.core.database.models import CalcResult, Mode
from src.ui import App
from src.utils.constants import dirs, CONFIG_PATH, DATABASE_URL


async def main(page: ft.Page) -> None:
    if not os.path.exists(CONFIG_PATH):
        cfg = cast(
            DictConfig,
            OmegaConf.create(
                f"""
TDX_INSTALL_DIR:
TDX_CACHE_DIR:
DATABASE_URL: {DATABASE_URL}
DEFAULT_EXTENSION: blk
BLOCK_PATH: tdxzs3.cfg
STOCK_PATH: tdxhy.cfg
ADDITIONAL_PATH: infoharbor_block.dat
                """
            ),
        )
        with open(CONFIG_PATH, "x", encoding="utf-8") as fp:
            OmegaConf.save(cfg, fp)

    else:
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
    Path(dirs.user_data_dir).mkdir(parents=True, exist_ok=True)
    ft.run(main)
