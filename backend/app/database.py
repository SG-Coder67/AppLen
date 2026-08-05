from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase,Session
from typing import Generator
from app.config import DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal=sessionmaker(bind=engine,
                          autoflush=False,
                          autocommit=False)
class Base(DeclarativeBase):
    pass
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
