# Import the FastAPI class from the fastapi package. FastAPI is the framework we are using to build our API service.

from fastapi import FastAPI

# Import the payment service which contains the business logic for processing transactions.

from app.services.payment_service import PaymentService

# Import the request model used to validate incoming payment requests

from app.models.payment_transaction import PaymentTransactionCreate

# Create an instance of the FastAPI application.
# This object represents our API server.
# All API routes (endpoints) will be attached to this object.

app = FastAPI()

# Initialize the payment service

payment_service = PaymentService()

# API enddpoint to create a payment transaction. This endpoint accepts a validated payment request and 
# sends it to payment service.

# Endpoint to create a payment

@app.post("/payments")


def create_payment(request: PaymentTransactionCreate):
    
    # Call the payment service to create the transaction.

    transaction = payment_service.create_transaction(request)

    # Return the created transaction to the client

    return transaction










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