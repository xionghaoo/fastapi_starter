from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.mysql_url, pool_pre_ping=True, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


