import os
from typing import Dict

import pandas as pd


def get_stocks(path: str | os.PathLike[str], mappings: Dict[str, str]) -> pd.DataFrame:
    try:
        df = pd.read_csv(
            path,
            sep="|",
            header=None,
            names=["0", "code", "code1", "code2", "code3", "code4"],
            dtype={"code": str},
        )
        df = df.dropna(
            subset=["code1", "code2", "code3", "code4"],
            how="all",
        )

        df["blocks"] = [
            [item for item in row if pd.notna(item)] for row in df[["code1", "code2", "code3", "code4"]].values
        ]
        stocks: pd.DataFrame = df[["code", "blocks"]].copy()

        stocks["blocks"] = stocks["blocks"].apply(lambda lst: [mappings[code] for code in lst if code in mappings])
        return stocks

    except FileNotFoundError:
        print(f"错误：文件 '{path}' 未找到。")
        return pd.DataFrame({})
    except UnicodeDecodeError:
        print(f"错误：文件 '{path}' 的编码可能不是 GBK。请检查文件编码。")
        return pd.DataFrame()
