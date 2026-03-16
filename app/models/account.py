# Import Enum to define controlled account types.
# Enum ensures that only valid account categories can exist.

from enum import Enum

# Import BaseModel from Pydantic.
# Pydantic models are used for API validation and structured data handling.

from pydantic import BaseModel

# AccountType defines the possible categories of financial accounts inside the payment platform ledger.

class AccountType(str, Enum):
    
    # Accounts representing users who send money.

    USER = "USER"

    # Accounts representing businesses or merchants receiving funds.

    MERCHANT = "MERCHANT"

    # Internal platform revenue account (fees collected).

    PLATFORM = "PLATFORM"

   # Temporary holding accounts used during settlement workflows.

    ESCROW = "ESCROW"

    # Account represents a ledger account in the system. Each account has an owner and a type.

    class Account(BaseModel)
        
        # Unique identifier for the account.

        account_is: str

        # Id of the entity that owns the account. This could represent a user, merchant, or internal platform entity

        owner_id: str

        # Type of account based on the AccountType enum.

        account_type: AccountType

        # Current account balance. This will eventually be calculated from ledger entries.

        balance: float = 0.0

 