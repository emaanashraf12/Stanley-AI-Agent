import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. "
        "PostgreSQL connection is required."
    )


if not DATABASE_URL.startswith(
    ("postgresql://", "postgres://")
):
    raise RuntimeError(
        "DATABASE_URL is not a PostgreSQL connection."
    )


print("DATABASE TYPE: POSTGRESQL")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()