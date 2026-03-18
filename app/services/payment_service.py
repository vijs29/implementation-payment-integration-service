# Import uuid so the platform can generate unique transaction IDs.
import uuid

# Import datetime to record when transactions were created.
from datetime import datetime

# Import SQLAlchemy session type used for database operations.
from sqlalchemy.orm import Session

# Import Decimal for precise financial calculations.
from decimal import Decimal, ROUND_HALF_UP

# Import ORM model for database persistence.
from app.database.models import PaymentTransactionDB

# Import domain models.
from app.models.payment_transaction import (
    PaymentTransaction,
    PaymentTransactionCreate,
    PaymentStatus
)

# Import ledger service to record financial entries.
from app.services.ledger_service import LedgerService

# Import ledger entry model.
from app.models.ledger_entry import LedgerEntry

# Import event publisher to push events to Redis.
from app.events.event_publisher import EventPublisher


class PaymentService:

    def __init__(self):
        self.ledger_service = LedgerService()
        self.publisher = EventPublisher()

    # ---------------------------------------------------
    # Duplicate check (DB-level)
    # ---------------------------------------------------
    def _check_duplicate_payment(self, request: PaymentTransactionCreate, db: Session):

        existing = db.query(PaymentTransactionDB).filter(
            PaymentTransactionDB.tenant_id == request.tenant_id,
            PaymentTransactionDB.property_id == request.property_id,
            PaymentTransactionDB.rent_year == request.rent_year,
            PaymentTransactionDB.rent_month == request.rent_month
        ).first()

        return existing is not None

    # ---------------------------------------------------
    # Platform fee calculation
    # ---------------------------------------------------
    def _calculate_platform_fee(self, amount: float, payment_channel):

        if payment_channel == "ACH":
            return Decimal("3.00")

        elif payment_channel == "CARD":
            amount_decimal = Decimal(str(amount))
            fee = (amount_decimal * Decimal("0.029")) + Decimal("0.30")
            return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        elif payment_channel == "CASH_AGENT":
            return Decimal("5.00")

        else:
            raise ValueError("Unsupported payment channel")

    # ---------------------------------------------------
    # Create Transaction
    # ---------------------------------------------------
    def create_transaction(self, request: PaymentTransactionCreate, db: Session):

        # ------------------------------------------
        # Step 0: Idempotency check
        # ------------------------------------------
        if request.idempotency_key:
            existing_txn = db.query(PaymentTransactionDB).filter(
                PaymentTransactionDB.idempotency_key == request.idempotency_key
            ).first()

            if existing_txn:
                print("Idempotent request detected, returning existing transaction")

                return PaymentTransaction(
                    transaction_id=existing_txn.transaction_id,
                    tenant_id=existing_txn.tenant_id,
                    property_id=existing_txn.property_id,
                    owner_id=existing_txn.owner_id,
                    rental_manager_id=existing_txn.rental_manager_id,
                    rent_year=existing_txn.rent_year,
                    rent_month=existing_txn.rent_month,
                    amount=existing_txn.amount,
                    currency=existing_txn.currency,
                    platform_fee=existing_txn.platform_fee,
                    net_settlement_amount=existing_txn.net_settlement_amount,
                    payment_channel=existing_txn.payment_channel,
                    status=existing_txn.status,
                    created_at=existing_txn.created_at
                )

        # ------------------------------------------
        # Step 1: Business duplicate check
        # ------------------------------------------
        if self._check_duplicate_payment(request, db):
            raise ValueError(
                "Duplicate payment detected for this tenant, property and rent period"
            )

        # ------------------------------------------
        # Step 2: Generate transaction
        # ------------------------------------------
        transaction_id = f"txn_{uuid.uuid4()}"
        created_at = datetime.utcnow()

        # ------------------------------------------
        # Step 3: Financial calculations
        # ------------------------------------------
        platform_fee = self._calculate_platform_fee(
            request.amount,
            request.payment_channel
        )

        amount_decimal = Decimal(str(request.amount))

        net_settlement_amount = (
            amount_decimal - platform_fee
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # ------------------------------------------
        # Step 4: Create domain object
        # ------------------------------------------
        transaction = PaymentTransaction(
            transaction_id=transaction_id,
            tenant_id=request.tenant_id,
            property_id=request.property_id,
            owner_id=request.owner_id,
            rental_manager_id=request.rental_manager_id,
            rent_year=request.rent_year,
            rent_month=request.rent_month,
            amount=request.amount,
            currency=request.currency,
            platform_fee=float(platform_fee),
            net_settlement_amount=float(net_settlement_amount),
            payment_channel=request.payment_channel,
            status=PaymentStatus.CREATED,
            created_at=created_at
        )

        # ------------------------------------------
        # Step 5: Ledger entries
        # ------------------------------------------
        tenant_account = f"acct_user_{request.tenant_id}"
        owner_account = f"acct_owner_{request.owner_id}"
        platform_account = "acct_platform_revenue"

        tenant_entry = LedgerEntry(
            entry_id="",
            transaction_id=transaction_id,
            account_id=tenant_account,
            debit=request.amount,
            credit=0
        )

        owner_entry = LedgerEntry(
            entry_id="",
            transaction_id=transaction_id,
            account_id=owner_account,
            debit=0,
            credit=float(net_settlement_amount)
        )

        platform_entry = LedgerEntry(
            entry_id="",
            transaction_id=transaction_id,
            account_id=platform_account,
            debit=0,
            credit=float(platform_fee)
        )

        self.ledger_service.record_entries(
            transaction_id,
            [tenant_entry, owner_entry, platform_entry],
            db
        )

        # ------------------------------------------
        # Step 6: Persist transaction
        # ------------------------------------------
        db_transaction = PaymentTransactionDB(
            transaction_id=transaction.transaction_id,
            tenant_id=transaction.tenant_id,
            property_id=transaction.property_id,
            owner_id=transaction.owner_id,
            rental_manager_id=transaction.rental_manager_id,
            rent_year=transaction.rent_year,
            rent_month=transaction.rent_month,
            amount=transaction.amount,
            currency=transaction.currency,
            platform_fee=transaction.platform_fee,
            net_settlement_amount=transaction.net_settlement_amount,
            payment_channel=transaction.payment_channel,
            status=transaction.status,
            created_at=transaction.created_at,
            idempotency_key=request.idempotency_key
        )

        db.add(db_transaction)

        # CRITICAL: Commit BEFORE publishing event
        db.commit()

        db.refresh(db_transaction)

        print(f"[DEBUG] Transaction committed: {transaction_id}")

        # ------------------------------------------
        # Step 7: Publish event (AFTER COMMIT)
        # ------------------------------------------
        event = {
            "event_type": "payment.created",
            "payload": {
                "transaction_id": transaction_id,
                "tenant_id": request.tenant_id,
                "owner_id": request.owner_id,
                "amount": request.amount,
                "currency": request.currency,
                "correlation_id": request.correlation_id
            }
        }

        print(f"[DEBUG] Publishing event for txn: {transaction_id}")

        self.publisher.publish(event)

        # ------------------------------------------
        # Step 8: Return response
        # ------------------------------------------
        return transaction