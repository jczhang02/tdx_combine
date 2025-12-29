import os

import pandas as pd
from sqlalchemy.orm import Session

from database import update_database
from reader import get_blocks, get_infoharbor_block_stock, get_re_code_relationship, get_stocks


def update_data(
    session: Session,
    TDX_CACHE_DIR: str | os.PathLike[str],
    BLOCK_PATH: str | os.PathLike[str],
    STOCK_PATH: str | os.PathLike[str],
    INFOHARBOR_PATH: str | os.PathLike[str],
    empty: bool = True,
) -> None:
    blocks_df: pd.DataFrame = get_blocks(path=os.path.join(TDX_CACHE_DIR, BLOCK_PATH))

    stocks_df: pd.DataFrame = get_stocks(
        path=os.path.join(TDX_CACHE_DIR, STOCK_PATH),
        mappings=get_re_code_relationship(blocks=blocks_df),
    )

    infoharbor_df: pd.DataFrame = get_infoharbor_block_stock(
        path=os.path.join(TDX_CACHE_DIR, INFOHARBOR_PATH),
    )

    assert not blocks_df.empty or not stocks_df.empty or not infoharbor_df.empty

    try:
        update_database(
            session=session,
            blocks_df=blocks_df,
            stocks_df=stocks_df,
            infoharbor_df=infoharbor_df,
            empty=empty,
        )
    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.close()
