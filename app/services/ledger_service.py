# ---------------------------------------------------
# LEDGER SERVICE
# ---------------------------------------------------

# Import uuid to generate unique identifiers
import uuid

# Import SQLAlchemy session
from sqlalchemy.orm import Session

# Import Decimal for financial precision
from decimal import Decimal

# Import Pydantic ledger model
from app.models.ledger_entry import LedgerEntry

# Import ORM DB model
from app.database.models import LedgerEntryDB


# ---------------------------------------------------
# LEDGER SERVICE CLASS
# ---------------------------------------------------
class LedgerService:
    """
    Handles creation and validation of ledger entries.

    Ensures:
    - Double-entry accounting integrity
    - Debit = Credit validation
    - Safe financial persistence
    """

    def record_entries(self, transaction_id: str, entries: list[LedgerEntry], db: Session):
        """
        Records ledger entries for a transaction.
        """

        # ------------------------------------------
        # STEP 1: Initialize totals using Decimal
        # ------------------------------------------
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        # ------------------------------------------
        # STEP 2: Aggregate values
        # ------------------------------------------
        for entry in entries:
            total_debit += Decimal(entry.debit)
            total_credit += Decimal(entry.credit)

        # ------------------------------------------
        # STEP 3: Validate double-entry accounting
        # ------------------------------------------
        if total_debit != total_credit:
            raise ValueError(
                f"Ledger imbalance detected: debit={total_debit}, credit={total_credit}"
            )

        # ------------------------------------------
        # STEP 4: Persist entries
        # ------------------------------------------
        for entry in entries:

            entry_id = f"entry_{uuid.uuid4()}"

            db_entry = LedgerEntryDB(
                entry_id=entry_id,
                transaction_id=transaction_id,
                account_id=entry.account_id,
                debit=Decimal(entry.debit),
                credit=Decimal(entry.credit),
                created_at=entry.created_at
            )

            db.add(db_entry)

        # ------------------------------------------
        # STEP 5: Commit transaction
        # ------------------------------------------
        db.commit()

        # ------------------------------------------
        # STEP 6: Debug visibility (important for tracing)
        # ------------------------------------------
        print(f"[LEDGER] Entries recorded for txn={transaction_id}")
        print(f"[LEDGER] Total Debit={total_debit}, Total Credit={total_credit}")

        return entries