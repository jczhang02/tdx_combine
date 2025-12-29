import os

import pandas as pd


def get_blocks(path: str | os.PathLike[str]) -> pd.DataFrame:
    try:
        blocks: pd.DataFrame = pd.read_csv(
            path,
            sep="|",
            header=None,
            names=["name", "code", "A", "B", "C", "re_code"],  # TODO: check ABC meanings and change name of variables
            encoding="gbk",
            dtype={"code": str},
        )
        blocks = blocks[["code", "name", "re_code", "A", "B", "C"]]
        return blocks

    except FileNotFoundError:
        print(f"错误：文件 '{path}' 未找到。")
        return pd.DataFrame({})
    except UnicodeDecodeError:
        print(f"错误：文件 '{path}' 的编码可能不是 GBK。请检查文件编码。")
        return pd.DataFrame()
