# Import uuid to generate unique identifiers for ledger entries.

import uuid


# Import SQLAlchemy session type used for database operations.

from sqlalchemy.orm import Session


# Import the Pydantic ledger entry model.

from app.models.ledger_entry import LedgerEntry


# Import the ORM database model representing the ledger_entries table.

from app.database.ledger_models import LedgerEntryDB


# LedgerService manages the creation and validation of ledger entries.
# It ensures that every financial transaction is balanced
# and records the entries in the database.


class LedgerService:

    # This method records ledger entries for a transaction.
    # It validates that total debits equal total credits before writing to the database.

    def record_entries(self, transaction_id: str, entries: list, db: Session):

        total_debit = 0.0
        total_credit = 0.0

        # Calculate total debit and credit values.

        for entry in entries:

            total_debit += entry.debit
            total_credit += entry.credit

        # Validate accounting balance.

        if round(total_debit, 2) != round(total_credit, 2):

            raise ValueError(
                "Ledger imbalance detected: total debits must equal total credits"
            )

        # Store entries in the database.

        for entry in entries:

            entry_id = f"entry_{uuid.uuid4()}"

            db_entry = LedgerEntryDB(
                entry_id=entry_id,
                transaction_id=transaction_id,
                account_id=entry.account_id,
                debit=entry.debit,
                credit=entry.credit,
                created_at=entry.created_at
            )

            # Add entry to database session.

            db.add(db_entry)

        # Commit all entries to the database.

        db.commit()

        # Return the recorded entries.

        return entries