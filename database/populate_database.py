from typing import List

import pandas as pd
from sqlalchemy import Tuple
from sqlalchemy.orm import Session

from .models import Block, Stock, stock_block_association


def empty_database(session: Session) -> None:
    session.query(stock_block_association).delete(synchronize_session=False)
    session.query(Stock).delete(synchronize_session=False)
    session.query(Block).delete(synchronize_session=False)


def blocks2database(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        block = Block(code=row["code"], name=row["name"])
        session.add(block)


def stocks2database(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        blocks_index: List[str] = row["blocks"]

        blocks = []
        for block_code in blocks_index:
            block = session.query(Block).filter(Block.code == block_code).one_or_none()
            blocks.append(block)

        stock = Stock(code=row["code"], region=row["region"], blocks=blocks)

        session.add(stock)


def infoharbor2database(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        stocks_index: List[Tuple[str, int]] = row["stocks"]
        block_code: str = row["code"]

        if not stocks_index:
            continue

        for stock_index in stocks_index:
            if not session.query(Stock).filter(Stock.code == stock_index[0]).one_or_none():
                stock = Stock(code=stock_index[0], region=stock_index[1])
                session.add(stock)

        session.flush()

        stocks_to_backroute = session.query(Stock).filter(Stock.code.in_([item[0] for item in stocks_index])).all()
        block = session.query(Block).filter(Block.code == block_code).one_or_none()

        if block and stocks_to_backroute:
            block.stocks.extend(stocks_to_backroute)


def update_database(
    session: Session,
    blocks_df: pd.DataFrame,
    stocks_df: pd.DataFrame,
    infoharbor_df: pd.DataFrame,
    empty: bool = True,
):
    if empty:
        empty_database(session=session)

    blocks2database(session=session, df=blocks_df)
    stocks2database(session=session, df=stocks_df)
    infoharbor2database(session=session, df=infoharbor_df)

    try:
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
