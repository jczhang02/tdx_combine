import os
from typing import List, Tuple

from sqlalchemy.orm import Session, joinedload

from database import Block


def export_combinations(
    path: str | os.PathLike[str],
    session: Session,
    ret: List[tuple],
) -> None:
    triplet: Tuple[str, str, str] = ret[0][0]

    NAME = ["A.blk", "B.blk", "C.blk"]

    for index, code in enumerate(triplet):
        save_name: str = os.path.join(path, NAME[index])

        block = session.query(Block).options(joinedload(Block.stocks)).filter(Block.code == code).one_or_none()
        stock_codes = [stock.code for stock in block.stocks]  # pyright: ignore

        with open(save_name, "w") as f:
            [f.write(str(item) + "\n") for item in stock_codes]
            f.close()
