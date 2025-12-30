from typing import List, TypedDict


class CombinationResultDict(TypedDict):
    blocks: List[str]
    stocks: List[str]
    count: int
