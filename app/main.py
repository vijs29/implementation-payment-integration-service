# FastAPI framework import used to create the API application and manage dependency injection.

from fastapi import FastAPI, Depends

# SQLAlchemy Session type used for database transactions.

from sqlalchemy.orm import Session

# Import the payment service which contains the core business
# logic for processing transactions.

from app.services.payment_service import PaymentService

# Import the request schema used to validate incoming
# payment transaction requests.

from app.models.payment_transaction import PaymentTransactionCreate

# Import the SQLAlchemy database engine and Base metadata
# used to initialize database tables.
# Also import get_db which provides a database session
# for each API request.

from app.database.database import engine, Base, get_db

# Import ORM table models so SQLAlchemy knows what
# database tables must exist when the application starts.

from app.database import models

Base.metadata.create_all(bind=engine)

# Import the balance service used to compute ledger balances.

from app.services.balance_service import BalanceService

# Create an instance of the FastAPI application.
# This object represents our API server.
# All API routes (endpoints) will be attached to this object.

app = FastAPI()

# Initialize the payment service

payment_service = PaymentService()

# Initiliaze balance service

balance_service = BalanceService()

# API enddpoint to create a payment transaction. This endpoint accepts a validated payment request and 
# sends it to payment service.

# Endpoint to create a payment

@app.post("/payments")


def create_payment(request: PaymentTransactionCreate, db: Session = Depends(get_db)):
    
    # Call the payment service to create the transaction.

    transaction = payment_service.create_transaction(request, db)

    # Return the created transaction to the client

    return transaction

# API endpoint to retrieve all payment transactions. This allows clients to view the transactions currently stored in the system.

@app.get("/payments")

#. Endpoint to retrieve the balance of an account from the ledger

def get_payments():

    # Return the list of stored transactions from the service.

    return payment_service.transactions


@app.get("/accounts/{account_id}/balance")

def get_account_balance(account_id: str, db: Session = Depends(get_db)):

    return balance_service.get_account_balance(account_id, db) 

# This decorator tells FastAPI that the function below
# should run when a GET request is sent to the "/health" endpoint.
# Decorators in Python modify the behavior of the function that follows.
# @app.get("/health")


# Define a Python function that will execute when the /health endpoint is called.
# "def" is the keyword used to define a function in Python.
# def health_check():

    # Return a dictionary containing the service status.
    # FastAPI automatically converts Python dictionaries into JSON responses.
    # This will be returned to the client calling the API.
    # return {"status": "Payment Integration Service running"}