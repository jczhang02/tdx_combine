import os
from itertools import combinations
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Block, stock_block_association


def check_blocks_in_database(
    code2id_mapping: Dict[str, int],
    blocks: List[str],
):
    print(code2id_mapping)

    found_codes = list(code2id_mapping.keys())
    if len(found_codes) != len(blocks):
        missing_codes = set(blocks) - set(found_codes)
        print(f"警告: 以下板块代码在数据库中未找到，将被忽略: {missing_codes}")


def get_combination_count(
    session: Session,
    path: str | os.PathLike[str],
) -> List[tuple]:
    with open(path, "r") as f:
        blocks: list[str] = list(f.read().split("\n"))

    block_info_query = session.query(Block.id, Block.code).filter(Block.code.in_(blocks))
    code2id_mapping = {code: id for id, code in block_info_query}

    check_blocks_in_database(
        code2id_mapping=code2id_mapping,
        blocks=blocks,
    )

    block_tuple = list(combinations(blocks, 3))
    results: dict = {}

    for code_triplet in block_tuple:
        id_triplet = [code2id_mapping[code] for code in code_triplet]
        query = (
            session.query(stock_block_association.c.stock_id)
            .filter(stock_block_association.c.block_id.in_(id_triplet))
            .group_by(stock_block_association.c.stock_id)
            .having(func.count(stock_block_association.c.block_id) == 3)
        )
        common_stock_count = query.count()
        results[code_triplet] = common_stock_count

    ret = sorted(results.items(), key=lambda item: item[1], reverse=True)
    return ret
