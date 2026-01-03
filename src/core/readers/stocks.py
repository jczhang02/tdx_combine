import os
from typing import Dict, List

import pandas as pd


def get_stocks(
    path: str | os.PathLike[str], mappings: Dict[str, str]
) -> List[dict]:
    """Function which provides a dict contains extracted information in TDXHY_PATH.

    Parameters
    ----------
    path : str | os.PathLike[str]
         Path of TDX stock file, which is always fixed as tdxhy.cfg.
    mappings : Dict[str, str]
         Dict retried from 'get_blocks' fuction.

    Returns
    -------
    List[dict]
        A dict contains information in TDXHY_PATH.

    """
    df = pd.read_csv(
        path,
        sep="|",
        header=None,
        names=["region", "code", "code1", "code2", "code3", "code4"],
        dtype={"code": str},
    )
    df = df.dropna(
        subset=["code1", "code2", "code3", "code4"],
        how="all",
    )

    df["blocks"] = [
        [item for item in row if pd.notna(item)]
        for row in df[["code1", "code2", "code3", "code4"]].values
    ]
    stocks: pd.DataFrame = df[["code", "region", "blocks"]].copy()

    stocks["blocks"] = stocks["blocks"].apply(
        lambda lst: [mappings[code] for code in lst if code in mappings]
    )
    return stocks.to_dict("records")
