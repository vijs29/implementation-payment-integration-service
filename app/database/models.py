# ---------------------------------------------------
# SQLALCHEMY ORM MODELS
# ---------------------------------------------------

# Import SQLAlchemy column types
from sqlalchemy import Column, String, DateTime, Numeric

# Import Base class used by ORM models
from app.database.database import Base

# Import datetime utilities for timestamping
from datetime import datetime, timezone


# ---------------------------------------------------
# LEDGER ENTRY TABLE (DOUBLE-ENTRY ACCOUNTING)
# ---------------------------------------------------
class LedgerEntryDB(Base):
    """
    Represents a financial ledger entry.

    Each payment transaction generates multiple ledger entries:
    - Tenant (debit)
    - Owner (credit)
    - Platform (credit)

    This ensures:
    - Financial accuracy
    - Auditability
    - Double-entry accounting integrity
    """

    __tablename__ = "ledger_entries"

    # PRIMARY KEY
    entry_id = Column(String, primary_key=True, index=True)

    # RELATIONSHIP FIELDS
    transaction_id = Column(String, index=True, nullable=False)
    account_id = Column(String, index=True, nullable=False)

    # FINANCIAL FIELDS (USE NUMERIC FOR PRECISION)
    debit = Column(Numeric(12, 2), default=0, nullable=False)
    credit = Column(Numeric(12, 2), default=0, nullable=False)

    # METADATA
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


# ---------------------------------------------------
# PAYMENT TRANSACTION TABLE
# ---------------------------------------------------
class PaymentTransactionDB(Base):
    """
    Represents a payment transaction in the system.

    Stores:
    - Tenant (payer)
    - Owner (receiver)
    - Amount and fees
    - Transaction lifecycle status
    """

    __tablename__ = "payment_transactions"

    # PRIMARY KEY
    transaction_id = Column(String, primary_key=True, index=True)

    # BUSINESS IDENTIFIERS
    tenant_id = Column(String, nullable=False)
    property_id = Column(String, nullable=False)
    owner_id = Column(String, nullable=False)
    rental_manager_id = Column(String, nullable=False)

    # BILLING PERIOD
    rent_year = Column(String, nullable=False)
    rent_month = Column(String, nullable=False)

    # FINANCIAL FIELDS
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, nullable=False)

    platform_fee = Column(Numeric(12, 2), nullable=False)
    net_settlement_amount = Column(Numeric(12, 2), nullable=False)

    # PAYMENT DETAILS
    payment_channel = Column(String, nullable=False)
    status = Column(String, nullable=False)

    # IDEMPOTENCY (CRITICAL FOR SAFE RETRIES)
    idempotency_key = Column(String, unique=True, index=True, nullable=True)

    # TIMESTAMP
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )