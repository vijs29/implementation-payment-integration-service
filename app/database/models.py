# SQLAlchemy column and data type definitions

from sqlalchemy import Column, String, Float, Integer, DateTime

# Import the Base class from database configuration

from app.database.database import Base

# ORM model representing the payment_transactions table

class PaymentTransactionDB(Base):
    
    # Name of the table in postgreSQL

    __tablename__ = "payment_transactions"

    # Primary transaction identifier

    transaction_id = Column(String, primary_key=True, index=True)

    # Tenant making the payment
    
    tenant_id = Column(String)

    # Property associated with the rent payment
    
    property_id = Column(String)

    # Property owner receiving settlement
    
    owner_id = Column(String)

    # Rental manager responsible for the property
    
    rental_manager_id = Column(String)

    # Billing period
    
    rent_year = Column(Integer)
    
    rent_month = Column(Integer)

    # Payment amount submitted by tenant
    
    amount = Column(Float)

    # Currency of payment
    
    currency = Column(String)

    # Platform revenue from the transaction
    
    platform_fee = Column(Float)

    # Amount transferred to property owner
    
    net_settlement_amount = Column(Float)

    # Payment method used
    
    payment_channel = Column(String)

    # Transaction lifecycle state
    
    status = Column(String)

    # Timestamp when transaction was created
    
    created_at = Column(DateTime)