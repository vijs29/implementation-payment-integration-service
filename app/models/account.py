# ---------------------------------------------------
# ACCOUNT DOMAIN MODELS
# ---------------------------------------------------

# Import Enum to define controlled account types.
# Ensures only valid account categories are used.
from enum import Enum

# Import BaseModel from Pydantic for data validation.
from pydantic import BaseModel


# ---------------------------------------------------
# ACCOUNT TYPE ENUM
# ---------------------------------------------------
class AccountType(str, Enum):
    """
    Defines the types of accounts in the system.
    """

    # Accounts representing users who send money
    USER = "USER"

    # Accounts representing merchants receiving funds
    MERCHANT = "MERCHANT"

    # Internal platform revenue account (fees)
    PLATFORM = "PLATFORM"

    # Temporary holding account (future use)
    ESCROW = "ESCROW"


# ---------------------------------------------------
# ACCOUNT MODEL
# ---------------------------------------------------
class Account(BaseModel):
    """
    Represents a ledger account in the payment system.
    """

    # Unique identifier for the account
    account_id: str

    # Owner of the account (user, merchant, or platform)
    owner_id: str

    # Type of account
    account_type: AccountType

    # Current balance (derived from ledger entries in future)
    balance: float = 0.0