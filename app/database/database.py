# SQLAlchemy provides the ORM framework used to interact with the database.

from sqlalchemy import create_engine

# sessionmaker is used to create database sessions that allow the application to 
# to execute queries and transactions

from sqlalchemy.orm import sessionmaker

# declarative_base is used to define ORM models(tables) using Python classes.

from sqlalchemy.orm import declarative_base

# Database connection string. This tells SQLAlchemy how to connect to PostgreSQL database.

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/payment_platform"

# Create the SQLAlchemy engine which manages connections to the database.

engine = create_engine(DATABASE_URL)

# SessionLocal is a factory used to create database sessions

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency used by FastAPI to provide a database session to API endpoints

def get_db():

    # Create a new db session.
    db = SessionLocal()

    try:

        # Provide the session to the API request

        yield db

    finally:
        # Ensure the session is closed after the requesst

        db.close()