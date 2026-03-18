# ---------------------------------------------------
# PAYMENT TRANSACTION DOMAIN MODELS
# ---------------------------------------------------

# Pydantic BaseModel for request/response validation
from pydantic import BaseModel

# Datetime for timestamps
from datetime import datetime

# Enum for controlled values
from enum import Enum

# Decimal for financial precision
from decimal import Decimal


# ---------------------------------------------------
# PAYMENT STATUS ENUM
# ---------------------------------------------------
class PaymentStatus(str, Enum):
    """
    Defines the lifecycle stages of a payment transaction.
    """

    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    AUTHORIZED = "AUTHORIZED"
    FAILED = "FAILED"
    SETTLED = "SETTLED"
    REFUNDED = "REFUNDED"


# ---------------------------------------------------
# PAYMENT CHANNEL ENUM
# ---------------------------------------------------
class PaymentChannel(str, Enum):
    """
    Defines how a payment is made.
    """

    ACH = "ACH"
    CARD = "CARD"
    CASH_AGENT = "CASH_AGENT"


# ---------------------------------------------------
# PAYMENT CREATE REQUEST MODEL
# ---------------------------------------------------
class PaymentTransactionCreate(BaseModel):
    """
    Incoming API request model for creating a payment.
    """

    tenant_id: str
    property_id: str
    owner_id: str
    rental_manager_id: str

    rent_year: int
    rent_month: int

    # NOTE: Still float here because request payloads are JSON
    amount: float

    currency: str

    # Use enum instead of raw string
    payment_channel: PaymentChannel

    # Idempotency key for safe retries
    idempotency_key: str | None = None

    # Correlation ID for observability / tracing
    correlation_id: str | None = None


# ---------------------------------------------------
# PAYMENT TRANSACTION RESPONSE MODEL
# ---------------------------------------------------
class PaymentTransaction(BaseModel):
    """
    Represents a fully processed payment transaction.
    """

    transaction_id: str

    tenant_id: str
    property_id: str
    owner_id: str
    rental_manager_id: str

    rent_year: int
    rent_month: int

    # Convert to Decimal internally for correctness
    amount: Decimal

    currency: str

    platform_fee: Decimal
    net_settlement_amount: Decimal

    payment_channel: PaymentChannel

    status: PaymentStatus

    created_at: datetime