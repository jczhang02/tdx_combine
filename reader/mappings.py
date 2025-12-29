from typing import Dict

import pandas as pd


def get_re_code_relationship(blocks: pd.DataFrame) -> Dict[str, str] | dict:
    try:
        mappings: Dict[str, str] = blocks.set_index(["re_code"])["code"].to_dict()
        return mappings
    except Exception as e:
        print(f"Error {e}")
        return {}
