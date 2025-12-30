TDX_CACHE_DIR: str = "./data/hq_cache/"  # NOTE: value need to be set at the first time

MODEL_PATH: str = "./data/Mode3.txt"  # NOTE: value via file picker

DATABASE_URL: str = "sqlite:///./data/model.db"
INFOHARBOR_PATH: str = "infoharbor_block.dat"
BLOCK_PATH: str = "tdxzs3.cfg"
STOCK_PATH: str = "tdxhy.cfg"

RET_SAVE_DIR: str = "./save"
DEFAULT_EXTENSION: str = "blk"

from action import export_combinations, get_combination_count, update_data
from database import setup_database

import time


def main():
    time1 = time.time()
    session = setup_database(DATABASE_URL=DATABASE_URL)
    update_data(
        session=session,
        TDX_CACHE_DIR=TDX_CACHE_DIR,
        BLOCK_PATH=BLOCK_PATH,
        STOCK_PATH=STOCK_PATH,
        INFOHARBOR_PATH=INFOHARBOR_PATH,
        empty=True,
    )
    time2 = time.time()
    ret = get_combination_count(
        session=session,
        path=MODEL_PATH,
    )

    export_combinations(
        path=RET_SAVE_DIR,
        ret=ret,
    )
    time3 = time.time()
    print(time2 - time1)
    print(time3 - time2)


if __name__ == "__main__":
    main()
