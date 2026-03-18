# ---------------------------------------------------
# FASTAPI APPLICATION ENTRYPOINT
# ---------------------------------------------------

# FastAPI framework used to build API endpoints
from fastapi import FastAPI, Depends

# SQLAlchemy session for DB access
from sqlalchemy.orm import Session

# Core business services
from app.services.payment_service import PaymentService
from app.services.balance_service import BalanceService

# Request schema
from app.models.payment_transaction import PaymentTransactionCreate

# Database setup
from app.database.database import engine, Base, get_db

# Import ORM models so tables are registered
from app.database import models

# Redis for shared metrics
import redis


# ---------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------
# Create tables if they do not exist
Base.metadata.create_all(bind=engine)


# ---------------------------------------------------
# REDIS CONFIGURATION (METRICS)
# ---------------------------------------------------
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

METRICS_KEY = "payment_metrics"


# ---------------------------------------------------
# FASTAPI APPLICATION SETUP
# ---------------------------------------------------
app = FastAPI(title="Payment Integration Service")


# Initialize services (stateless singletons)
payment_service = PaymentService()
balance_service = BalanceService()


# ---------------------------------------------------
# PAYMENT ENDPOINTS
# ---------------------------------------------------
@app.post("/payments")
def create_payment(
    request: PaymentTransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new payment.

    Flow:
    - Validate request
    - Process transaction
    - Persist to DB
    - Publish async event
    """
    return payment_service.create_transaction(request, db)


# ---------------------------------------------------
# ACCOUNT / LEDGER ENDPOINTS
# ---------------------------------------------------
@app.get("/accounts/{account_id}/balance")
def get_account_balance(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Get account balance from ledger.

    balance = credits - debits
    """
    return balance_service.get_account_balance(account_id, db)


# ---------------------------------------------------
# METRICS (OBSERVABILITY)
# ---------------------------------------------------
@app.get("/metrics")
def get_metrics():
    """
    Returns system metrics from Redis.

    Safe against missing/null values.
    """
    try:
        metrics = redis_client.hgetall(METRICS_KEY)

        return {
            "events_processed": int(metrics.get("events_processed") or 0),
            "events_failed": int(metrics.get("events_failed") or 0),
            "events_retried": int(metrics.get("events_retried") or 0),
            "events_dlq": int(metrics.get("events_dlq") or 0),
        }

    except Exception as e:
        return {
            "error": str(e),
            "raw_metrics": redis_client.hgetall(METRICS_KEY)
        }


# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------
@app.get("/health")
def health_check():
    """
    Health endpoint for:
    - Load balancers
    - Kubernetes probes
    """
    return {"status": "Payment Integration Service running"}