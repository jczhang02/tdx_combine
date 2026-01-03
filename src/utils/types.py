from typing import Any, List, Optional, TypedDict


class CombinationResultDict(TypedDict):
    blocks: List[str]
    stocks: List[str]
    count: int


class StockDict(TypedDict):
    code: str
    region: int


class InfoharborDataDict(TypedDict):
    code: str
    name: str
    stocks: List[StockDict]


class Response(TypedDict):
    code: int
    message: str
    data: Optional[Any]
