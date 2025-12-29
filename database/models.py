from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

stock_block_association = Table(
    "stock_block_association",
    Base.metadata,
    Column("stock_id", Integer, ForeignKey("stocks.id"), primary_key=True, nullable=False),
    Column("block_id", Integer, ForeignKey("blocks.id"), primary_key=True, nullable=False),
)


class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    blocks = relationship("Block", secondary=stock_block_association, back_populates="stocks")

    def __repr__(self):
        return f"<Stock(code='{self.code}')>"


class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    stocks = relationship("Stock", secondary=stock_block_association, back_populates="blocks")

    def __repr__(self):
        return f"<Block(code='{self.code}', name='{self.name}')>"
