from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager
from app import settings
from app.models import Base
from typing import Iterator

engine = create_engine(settings.DB_URL, pool_pre_ping=True, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session() -> Iterator[Session]:
    with SessionLocal() as db:

        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Transaction Failed: {e}")
        finally:
            db.close()


def get_db():
    with SessionLocal() as db:

        try:
            yield db
        finally:
            db.close()
