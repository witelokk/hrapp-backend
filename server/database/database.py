from os import environ
from typing import Annotated
from fastapi import Depends
from sqlalchemy import URL, StaticPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base


from ..settings import get_settings


url = URL.create(
    "postgresql",
    get_settings().postgres_username,
    get_settings().postgres_password,
    get_settings().postgres_host,
    get_settings().postgres_port,
)

engine = create_engine(
    url, connect_args={}, poolclass=StaticPool, echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
