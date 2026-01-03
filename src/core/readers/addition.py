import os
import re
from typing import Dict, List, Pattern


def get_addition(path: str | os.PathLike[str]) -> List[dict]:
    """Function which provides a list contains extracted addition information in INFOHARBOR_PATH.

    Parameters
    ----------
    path : str | os.PathLike[str]
         Path of TDX addition file, which is always fixed as "infoharbor_block.dat".

    Returns
    -------
    List[dict]
        A list contains addition information.

    """
    addition = []

    cur_name: str = ""
    cur_code: str = ""
    cur_stocks: List[Dict[str, int | str]] = []

    block_start_pattern: Pattern[str] = re.compile(r"#[a-zA-Z]+_([^,]+)")

    with open(path, "r", encoding="gbk") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            match = block_start_pattern.match(line)

            if match:
                if cur_code and cur_name and cur_stocks:
                    addition.append(
                        {
                            "code": cur_code,
                            "name": cur_name,
                            "stocks": cur_stocks,
                        }
                    )

                new_block_name = match.group(1).strip()
                parts = line.split(",")
                new_block_code = parts[2].strip() if len(parts) > 2 else ""

                cur_name = new_block_name
                cur_code = new_block_code
                cur_stocks = []
            else:
                stock_parts: List[str] = [
                    code.strip() for code in line.split(",") if code.strip()
                ]

                for stock_part in stock_parts:
                    if "#" in stock_part:
                        splited: List[str] = stock_part.split(
                            sep="#",
                            maxsplit=1,
                        )
                        cur_stocks.append(
                            {
                                "code": splited[1],
                                "region": int(splited[0]),
                            }
                        )

        if cur_code and cur_name and cur_stocks:
            addition.append(
                {
                    "code": cur_code,
                    "name": cur_name,
                    "stocks": cur_stocks,
                }
            )

    return addition
