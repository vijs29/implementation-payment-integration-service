# Import SQLAlchemy session for database access.

from sqlalchemy.orm import Session

# Import database ledger model

from app.database.ledger_models import LedgerEntryDB

# BalanceService calculates account balances from ledger entries.

class BalanceService:
    # Compute balance for a given account

    def get_account_balance(self, account_id: str, db:Session):

        # Fetch all ledger entries for the account.

        entries = db.query(LedgerEntryDB).filter(
            LedgerEntryDB.account_id == account_id
        ).all()

        total_debit = 0
        total_credit = 0

        for entry in entries:
            total_debit += entry.debit
            total_credit += entry.credit

        # Balance formula used by financial ledgers.

        balance = total_credit - total_debit

        return {

            "account_id": account_id,
            "balance": balance
        }