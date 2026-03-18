# ---------------------------------------------------
# SQLALCHEMY DATABASE CONFIGURATION
# ---------------------------------------------------

# SQLAlchemy engine is used to manage DB connections
from sqlalchemy import create_engine

# sessionmaker creates DB sessions (transactions)
from sqlalchemy.orm import sessionmaker

# Base class for all ORM models (tables)
from sqlalchemy.orm import declarative_base


# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------
# Connection string for PostgreSQL
# Format: postgresql://<user>@<host>:<port>/<database>
DATABASE_URL = "postgresql://vijnewmac@localhost:5432/payment_platform"


# ---------------------------------------------------
# ENGINE CONFIGURATION
# ---------------------------------------------------
# Engine manages connection pool and DB connectivity
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Ensures stale connections are detected and refreshed
    pool_size=5,          # Default connection pool size
    max_overflow=10       # Extra connections allowed beyond pool_size
)


# ---------------------------------------------------
# SESSION FACTORY
# ---------------------------------------------------
# SessionLocal is used to create a new DB session per request
SessionLocal = sessionmaker(
    autocommit=False,   # We control commits manually
    autoflush=False,    # Prevents auto flush before queries
    bind=engine
)


# ---------------------------------------------------
# BASE CLASS FOR ORM MODELS
# ---------------------------------------------------
Base = declarative_base()


# ---------------------------------------------------
# FASTAPI DEPENDENCY
# ---------------------------------------------------
# Provides a DB session to each API request
def get_db():
    """
    Dependency that provides a database session.

    Ensures:
    - Each request gets its own session
    - Session is properly closed after request completes
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()