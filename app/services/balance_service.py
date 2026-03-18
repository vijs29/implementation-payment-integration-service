# ---------------------------------------------------
# BALANCE SERVICE
# ---------------------------------------------------

# Import SQLAlchemy session for database access
from sqlalchemy.orm import Session

# Import Decimal for precise financial calculations
from decimal import Decimal

# Import database ledger model
from app.database.models import LedgerEntryDB


# ---------------------------------------------------
# BALANCE SERVICE CLASS
# ---------------------------------------------------
class BalanceService:
    """
    Calculates account balances using ledger entries.

    Balance formula:
        balance = total_credit - total_debit
    """

    def get_account_balance(self, account_id: str, db: Session):
        """
        Compute balance for a given account.
        """

        # Fetch all ledger entries for the account
        entries = db.query(LedgerEntryDB).filter(
            LedgerEntryDB.account_id == account_id
        ).all()

        # Initialize totals using Decimal for accuracy
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        # Aggregate ledger entries
        for entry in entries:
            total_debit += Decimal(entry.debit or 0)
            total_credit += Decimal(entry.credit or 0)

        # Calculate final balance
        balance = total_credit - total_debit

        return {
            "account_id": account_id,
            "balance": float(balance)  # Convert for API response
        }