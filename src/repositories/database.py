from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def create_database(
    database_url: str,
):
    connect_args = {}

    if database_url.startswith(
        "sqlite"
    ):
        connect_args = {
            "check_same_thread": False
        }

    engine = create_engine(
        database_url,
        connect_args=connect_args,
    )

    Base.metadata.create_all(
        engine
    )

    return engine


def create_session_factory(
    database_url: str,
):
    engine = create_database(
        database_url
    )

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )