# Import uuid so the platform can generate unique transaction 
# IDs.
# Each payment transaction must have a globally unique
# identifier.

import uuid

# Import datetime to record when transactions were created.

from datetime import datetime

# Import the transaction models we created earlier.
# These models define the structure of payment requests.
# and stored transaction records.

from app.models.payment_transaction import(
    PaymentTransaction,
    PaymentTransactionCreate,
    PaymentStatus 
)

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

    
    def create_transaction(self, request:PaymentTransactionCreate):
        
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

        # Store the transaction in the in-memory transaction list.

        self.transactions.append(transaction)

        # Return the created transaction so the API layer can 
        # send it back to the client

        return transaction 