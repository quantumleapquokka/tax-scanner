from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = "sqlite:///./tax_scanner.db"


class Base(DeclarativeBase):
    """
    Base class inherited by all SQLAlchemy database models.
    """

    pass


# SQLite requires this option when used by a web application that may access the database across different request-handling threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Creates database sessions used to query and modify stored records.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)