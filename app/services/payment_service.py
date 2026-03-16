# Import uuid so the platform can generate unique transaction IDs.
# Each payment transaction must have a globally unique identifier.

import uuid

# Import datetime to record when transactions were created.

from datetime import datetime

# Import SQLAlchemy session type used for database operations.

from sqlalchemy.orm import Session

# Import the ORM database model representing the database table.

from app.database.models import PaymentTransactionDB

# Import the transaction models we created earlier.
# These models define the structure of payment requests.
# and stored transaction records.

from app.models.payment_transaction import(
    PaymentTransaction,
    PaymentTransactionCreate,
    PaymentStatus 
)

# Import ledger service to record financial entries.

from app.services.ledger_service import LedgerService

# Import ledger entry model

from app.models.ledger_entry import LedgerEntry

# PaymentService contains the core business logic for
# handling payment transactions in the platform.
#
# The service layer is responsible for tasks such as:
# - creating new transactions
# - calculating platform fee
# - preventing duplicate rent payments
# - initializing transaction lifecycle state

class PaymentService:

    # The constructor runs when the service is initialized.
    # For now we will create an in-memory list to simulate
    # a transaction store until we add a real database.

    def __init__(self):
        
        # Temporary storage for transactions
        # Later this will be replaced by a database.

        self.transactions = []

        # Initialize the ledger service used to record accounting entries.

        self.ledger_service = LedgerService()

    # This method checks whether a payment already exists for the same tenant, property and rent 
    # billing period

    def _check_duplicate_payment(self, request: PaymentTransactionCreate):

        # Loop through all stored transactions:

        for transaction in self.transactions:

            # check if tenant, property and billingperiod match.

            if(
                transaction.tenant_id == request.tenant_id
                and transaction.property_id == request.property_id
                and transaction.rent_year == request.rent_year
                and transaction.rent_month == request.rent_month
            ):
                return True
            
        # If no duplicate found, return False.

        return False 
        
    # This method calculates the platform fee based on the payment channel used by the tenant.
    #
    # Different channels have different fee structures.

    def _calculate_platform_fee(self, amount: float, payment_channel):
        
        # ACH payments have a small flat processing fee.

        if payment_channel == "ACH":
            return 3.0
        
        # Card payments usually have a percentage fees plus a small fixed processing cost

        elif payment_channel == "CARD":
            return amount * 0.029 + 0.30
        
        # Cash agent payments havea higher flat handling fee.

        elif payment_channel == "CASH_AGENT":
            return 5.0
        
        # If an unknown payment channel is used, raise an error to prevent invalid processing.

        else:
            raise ValueError("Unsupported payment channel")
        
    
    # This method creates a new payment transaction. It accepts a validated PaymentTransactionCreate object
    # coming from the API layer
    # Create a new payment transaction and persist it in the PostgreSQL database.
    
    def create_transaction(self, request:PaymentTransactionCreate, db:Session):
        
        # Check if a payment already exists for this tenant, property and billing period.

        if self._check_duplicate_payment(request):

            # If a duplicate payment is detected, stop processing and raise an error.

            raise ValueError(
                "Duplicate payment detected for this tenant, property and rent period"
            )
                  
        # Generate a unique transaction ID using UUID.    

        transaction_id = f"txn_{uuid.uuid4()}"

        # Record the timestamp when the transaction was
        # created

        created_at = datetime.utcnow()

        # Calculate the platform fee based on the payment channel.

        platform_fee = self._calculate_platform_fee(
            request.amount,
            request.payment_channel
        )
        
        # Calculate the net amount that will be settled to the property owner after deducting the fee.

        net_settlement_amount = request.amount - platform_fee

        # Create the PaymentTransaction object using the data
        # from the request and system-generated fields.

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
            platform_fee=platform_fee,
            net_settlement_amount=net_settlement_amount,
            payment_channel=request.payment_channel,
            status=PaymentStatus.CREATED,
            created_at=created_at 
        )

        # Define ledger accounts involved in this payment.

        tenant_account = f"account_user_{request.tenant_id}"

        owner_account = f"acct_merchant{request.owner_id}"

        platform_account = "acct_platform_revenue"

        # Tenant account debit(money leaving tenant)

        tenant_entry = LedgerEntry(
           entry_id="",
           transaction_id=transaction_id,
           account_id=tenant_account,
           debit=request.amount,
           credit=0 
        )

        # Owner account credit( money received after platform fee)

        owner_entry = LedgerEntry(
            entry_id="",
            transaction_id=transaction_id,
            account_id=owner_account,
            debit=0,
            credit=net_settlement_amount

        )

        # platform revenue credit

        platform_entry = LedgerEntry(
            entry_id="",
            transaction_id=transaction_id,
            account_id=platform_account,
            debit=0,
            credit=platform_fee
        )

        # Record ledger entries and enforce debit/credit balance.

        self.ledger_service.record_entries(
            transaction_id,
            [tenant_entry, owner_entry, platform_entry],
            db
        )

        # Convert the domain transaction object into the ORM database model.
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
             created_at=transaction.created_at
        )

        # Add the transaction to the database session.
        db.add(db_transaction)

        # Commit the transaction so it is written to PostgreSQL.
        db.commit()

        # Refresh the object so SQLAlchemy loads the stored state.
        db.refresh(db_transaction)

        # Return the created transaction so the API layer can send it back to the client

        return transaction 