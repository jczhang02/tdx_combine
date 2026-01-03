import os
from typing import Dict, List, Tuple

import pandas as pd

from .helpers import get_re_code_relationship


def get_blocks(
    path: str | os.PathLike[str],
) -> Tuple[List[dict], Dict[str, str]]:
    """Function which provides a dict contains extracted block information and a code mapping in TDXZS_PATH.
    Exactly, the information consists of block name, block code, several no-meaning columns, and another block code "re_code".
    Since "re_code" is used in TDXHY_PATH, the code mapping is necessary.


    Parameters
    ----------
    path : str | os.PathLike[str]
         Path of TDX block file, which is always fixed as tdxzs3.cfg.

    Returns
    -------
    Tuple[List[dict], Dict[str, str]]
        A tuple contains information in TDXZS_PATH and mapping.

    """
    blocks: pd.DataFrame = pd.read_csv(
        path,
        sep="|",
        header=None,
        names=[
            "name",
            "code",
            "A",
            "B",
            "C",
            "re_code",
        ],  # TODO: check ABC meanings and change name of variables
        encoding="gbk",
        dtype={"code": str},
    )
    blocks = blocks[["code", "name", "re_code", "A", "B", "C"]]
    return (
        blocks[["code", "name"]].to_dict("records"),
        get_re_code_relationship(blocks=blocks),
    )
