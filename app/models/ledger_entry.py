# Import datetime to timestamp ledger activity.

from datetime import datetime, timezone

# Import BaseModel from Pydantic.
# This is used to validate structured data in our application.

from pydantic import BaseModel

# LedgerEntry represents a single debit or credit movement inside the financial ledger.

class LedgerEntry(BaseModel):

    # Unique identifier for the ledger entry.

    entry_id: str

    # Transaction this ledger entry belongs to.

    transaction_id: str

    # Account affected by this ledger entry.

    account_id: str

    # Debit amount(money leaving the account)

    debit: float = 0.0

    # Credit amount(money entering the account)

    credit: float = 0.0

    # Timestamp when the entry was created. Uses timezone-aware UTC timestamp.

    created_at: datetime = datetime.now(timezone.utc)

    