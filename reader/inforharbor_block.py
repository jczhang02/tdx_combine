import os
import re
from typing import Dict, List, Pattern, Union

import pandas as pd
from rich import print


def get_infoharbor_block_stock(path: str | os.PathLike[str]) -> pd.DataFrame:
    block_records: List[Dict[str, Union[str, List[str]]]] = []

    cur_name: str = ""
    cur_code: str = ""
    cur_stocks: list[str] = []

    block_start_pattern: Pattern[str] = re.compile(r"#[a-zA-Z]+_([^,]+)")

    try:
        with open(path, "r", encoding="gbk") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                match = block_start_pattern.match(line)

                if match:
                    if cur_code and cur_name and cur_stocks:
                        block_records.append({"code": cur_code, "name": cur_name, "stocks": cur_stocks})

                    # Then, reset state variables for the new block.
                    new_block_name = match.group(1).strip()
                    parts = line.split(",")
                    new_block_code = parts[2].strip() if len(parts) > 2 else ""

                    cur_name = new_block_name
                    cur_code = new_block_code
                    cur_stocks = []
                else:
                    codes = [code.strip().split("#")[-1] for code in line.split(",") if code.strip()]
                    cur_stocks.extend(codes)

            if cur_code and cur_name and cur_stocks:
                block_records.append({"code": cur_code, "name": cur_name, "stocks": cur_stocks})

            if not block_records:
                return pd.DataFrame()

        blocks = pd.DataFrame(block_records)
        blocks = blocks.sort_values("code").reset_index(drop=True)

        return blocks

    except Exception as e:
        print(f"[bold red]An error occurred while parsing the file: {e}[/bold red]")
        return pd.DataFrame()
