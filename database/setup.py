from sqlalchemy import (
    URL,
    Engine,
    create_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def setup_database(DATABASE_URL: str | URL) -> Session:
    engine: Engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    return session
