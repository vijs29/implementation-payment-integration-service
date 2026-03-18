# ---------------------------------------------------
# LEDGER ENTRY DOMAIN MODEL
# ---------------------------------------------------

# Import datetime to timestamp ledger activity
from datetime import datetime, timezone

# Import Decimal for precise financial representation
from decimal import Decimal

# Import BaseModel from Pydantic
from pydantic import BaseModel


# ---------------------------------------------------
# LEDGER ENTRY MODEL
# ---------------------------------------------------
class LedgerEntry(BaseModel):
    """
    Represents a single debit or credit entry in the ledger.

    Every financial transaction is broken into:
    - Debit entries (money leaving)
    - Credit entries (money entering)

    This enables:
    - Double-entry accounting
    - Auditability
    - Financial correctness
    """

    # Unique identifier for the ledger entry
    entry_id: str

    # Transaction this entry belongs to
    transaction_id: str

    # Account affected
    account_id: str

    # Debit amount (money leaving the account)
    debit: Decimal = Decimal("0.00")

    # Credit amount (money entering the account)
    credit: Decimal = Decimal("0.00")

    # Timestamp (UTC, timezone-aware)
    created_at: datetime = datetime.now(timezone.utc)