import os
from typing import List

from utils import CombinationResultDict


def export_combinations(
    path: str | os.PathLike[str],
    ret: List[CombinationResultDict],
) -> None:
    if len(ret) != 3:
        raise RuntimeError("combination results is not equal to 3")

    NAME: List[str] = ["ZH1.blk", "ZH2.blk", "ZH3.blk"]

    for index, part in enumerate(ret):
        save_name: str = os.path.join(path, NAME[index])

        blocks: List[str] = part["blocks"]
        stocks: List[str] = part["stocks"]

        with open(save_name, "w") as f:
            for block in blocks:
                f.write(str(block) + "\n")

            for stock in stocks:
                f.write(str(stock) + "\n")

        f.close()
