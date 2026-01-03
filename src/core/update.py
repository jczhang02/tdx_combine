import concurrent.futures
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database import update_database
from src.core.readers import get_addition, get_blocks, get_stocks
from src.utils.types import Response


async def update_data(
    async_session: async_sessionmaker[AsyncSession],
    TDX_CACHE_DIR: str | os.PathLike[str],
    BLOCK_PATH: str | os.PathLike[str],
    STOCK_PATH: str | os.PathLike[str],
    ADDITIONAL_PATH: str | os.PathLike[str],
    is_clear: bool = True,
) -> Response:
    """action function for updating TDX data from cache.

    Parameters
    ----------
    async_session : async_sessionmaker[AsyncSession]
        Asyncio version of Session.
    TDX_CACHE_DIR : str | os.PathLike[str]
        Path of TDX cache dir.
    BLOCK_PATH : str | os.PathLike[str]
        Path of TDX block file, which is always fixed as tdxzs3.cfg.
    STOCK_PATH : str | os.PathLike[str]
        Path of TDX stock file, which is always fixed as tdxhy.cfg.
    ADDITIONAL_PATH : str | os.PathLike[str]
        Path of TDX addition file, which is always fixed as infoharbor_block.dat.
        Exactly, the file contains concept block informations mainly.
    is_clear : bool
        Whether to clear database before excute the action.

    Returns
    -------
    Response
        API Response used for flet.

    """
    TDXZS_PATH: str = os.path.join(TDX_CACHE_DIR, BLOCK_PATH)
    TDXHY_PATH: str = os.path.join(TDX_CACHE_DIR, STOCK_PATH)
    INFOHARBOR_PATH: str = os.path.join(TDX_CACHE_DIR, ADDITIONAL_PATH)

    try:
        blocks, mappings = get_blocks(path=TDXZS_PATH)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_stocks = executor.submit(
                get_stocks,
                TDXHY_PATH,
                mappings,
            )
            future_addition = executor.submit(
                get_addition,
                INFOHARBOR_PATH,
            )

            stocks = future_stocks.result()
            addition = future_addition.result()

        if not blocks or not stocks or not addition:
            raise RuntimeError("Dataframe empty")

        await update_database(
            async_session=async_session,
            blocks=blocks,
            stocks=stocks,
            addition=addition,
            is_clear=is_clear,
        )

        return Response(
            code=200,
            message="Success",
            data=None,
        )

    except Exception as e:
        return Response(
            code=300,
            message=f"更新数据中出现问题: {e}",
            data=None,
        )
