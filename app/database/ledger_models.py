# Import SQLAlchemy column types.

from sqlalchemy import Column, String, Float, DateTime


# Import Base class used by ORM models.

from app.database.database import Base


# Import datetime utilities.

from datetime import datetime, timezone


# ORM model representing the ledger_entries table.


class LedgerEntryDB(Base):

    # Table name in PostgreSQL

    __tablename__ = "ledger_entries"

    # Unique identifier for the ledger entry

    entry_id = Column(String, primary_key=True, index=True)

    # Transaction this entry belongs to

    transaction_id = Column(String, index=True)

    # Account affected

    account_id = Column(String, index=True)

    # Debit amount

    debit = Column(Float)

    # Credit amount

    credit = Column(Float)

    # Timestamp

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))