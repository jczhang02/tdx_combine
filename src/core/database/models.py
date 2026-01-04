from datetime import datetime
from typing import List

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
    select,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship


class Base(DeclarativeBase):
    pass


stock_block_association = Table(
    "stock_block_association",
    Base.metadata,
    Column(
        "stock_id",
        Integer,
        ForeignKey("stocks.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "block_id",
        Integer,
        ForeignKey("blocks.id"),
        primary_key=True,
        nullable=False,
    ),
)


class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    region = Column(Integer, unique=False, nullable=False)
    name = Column(String(100), unique=False, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    blocks: Mapped[List["Block"]] = relationship(
        "Block",
        secondary=stock_block_association,
        back_populates="stocks",
    )

    def __repr__(self):
        return f"<Stock(code='{self.code}')>"


class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    stocks: Mapped[List["Stock"]] = relationship(
        "Stock", secondary=stock_block_association, back_populates="blocks"
    )

    @hybrid_property
    def stock_count(self) -> int:
        """返回该板块包含的股票数量 - Python 对象级别"""
        return len(self.stocks)

    @stock_count.expression
    def _stock_count_expression(cls):
        """返回该板块包含的股票数量 - SQL 查询级别"""
        return (
            select(func.count(stock_block_association.c.stock_id))
            .where(stock_block_association.c.block_id == cls.id)
            .scalar_subquery()
        )

    def __repr__(self):
        return f"<Block(code='{self.code}', name='{self.name}')>"


class Mode(Base):
    __tablename__: str = "mode"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), unique=False, nullable=True)
    count = Column(Integer, unique=False, nullable=False)


class CalcResult(Base):
    __tablename__: str = "calc_result"
    id = Column(Integer, primary_key=True, autoincrement=True)
    blocks = Column(JSON, nullable=False)
    stocks = Column(JSON, nullable=False)
    count = Column(Integer, nullable=False)
