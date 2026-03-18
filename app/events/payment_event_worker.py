# ---------------------------------------------------
# PAYMENT EVENT WORKER
# ---------------------------------------------------

import redis
import json
import time
import logging

from app.database.database import SessionLocal
from app.database.models import PaymentTransactionDB
from app.services.payment_state_machine import PaymentStateMachine
from app.models.payment_transaction import PaymentStatus


# ---------------------------------------------------
# LOGGING CONFIG (STRUCTURED LOGS)
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-worker")


# ---------------------------------------------------
# REDIS CONFIG
# ---------------------------------------------------
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

METRICS_KEY = "payment_metrics"
DLQ_METRIC_FIELD = "events_dlq"


# ---------------------------------------------------
# WORKER LOOP
# ---------------------------------------------------
def start_worker():

    logger.info("Payment event worker started. Waiting for events..")

    while True:

        event = redis_client.brpop(["payment_events", "payment_events_retry"])

        if event:

            queue_name, event_data = event

            event_payload = json.loads(event_data)

            # ✅ FIXED: inside correct scope
            logger.info(json.dumps({
                "message": "event_received",
                "queue": queue_name,
                "event": event_payload
            }))

            try:
                process_event(event_payload)

            except Exception as e:
                logger.error(json.dumps({
                    "message": "event_processing_failed",
                    "error": str(e),
                    "event": event_payload
                }))

                redis_client.hincrby(METRICS_KEY, "events_failed", 1)
                retry_event(event_payload)


# ---------------------------------------------------
# PROCESS EVENT
# ---------------------------------------------------
def process_event(event):

    event_type = event.get("event_type")
    payload = event.get("payload") or {}

    correlation_id = payload.get("correlation_id", "N/A")
    transaction_id = payload.get("transaction_id")

    if not transaction_id:
        logger.error(f"[{correlation_id}] Missing transaction_id")
        return

    db = SessionLocal()

    try:

        if event_type == "payment.created":

            # Simulated failure
            if payload.get("tenant_id") == "fail_test":
                raise Exception("Simulated failure")

            logger.info(f"[{correlation_id}] Processing txn: {transaction_id}")

            # ----------------------------------------
            # RETRY LOOKUP
            # ----------------------------------------
            transaction = None

            for attempt in range(5):

                logger.info(f"[{correlation_id}] Lookup attempt {attempt+1}")

                transaction = db.query(PaymentTransactionDB).filter(
                    PaymentTransactionDB.transaction_id == transaction_id
                ).first()

                if transaction:
                    break

                time.sleep(0.5)

            if not transaction:
                logger.error(f"[{correlation_id}] Transaction not found: {transaction_id}")
                return

            # Normalize DB value → Enum
            current_status = PaymentStatus(transaction.status)

            # ----------------------------------------
            # DUPLICATE PROTECTION
            # ----------------------------------------
            if current_status in [
                PaymentStatus.PROCESSING,
                PaymentStatus.AUTHORIZED,
                PaymentStatus.SETTLED
            ]:
                logger.info(f"[{correlation_id}] Skipping already processed txn")
                return

            # ----------------------------------------
            # STEP 1: PROCESSING
            # ----------------------------------------
            PaymentStateMachine.validate_transition(
                current_status,
                PaymentStatus.PROCESSING
            )

            transaction.status = PaymentStatus.PROCESSING.value
            db.commit()

            logger.info(f"[{correlation_id}] Status → PROCESSING")

            # ----------------------------------------
            # STEP 2: AUTHORIZED
            # ----------------------------------------
            current_status = PaymentStatus(transaction.status)

            PaymentStateMachine.validate_transition(
                current_status,
                PaymentStatus.AUTHORIZED
            )

            transaction.status = PaymentStatus.AUTHORIZED.value
            db.commit()

            logger.info(f"[{correlation_id}] Status → AUTHORIZED")

            time.sleep(2)

            # ----------------------------------------
            # STEP 3: SETTLED
            # ----------------------------------------
            current_status = PaymentStatus(transaction.status)

            PaymentStateMachine.validate_transition(
                current_status,
                PaymentStatus.SETTLED
            )

            transaction.status = PaymentStatus.SETTLED.value
            db.commit()

            logger.info(f"[{correlation_id}] Status → SETTLED")

            # ----------------------------------------
            # METRICS
            # ----------------------------------------
            redis_client.hincrby(METRICS_KEY, "events_processed", 1)

        else:
            logger.warning(f"[{correlation_id}] Unhandled event type: {event_type}")

    finally:
        db.close()


# ---------------------------------------------------
# RETRY + DLQ
# ---------------------------------------------------
def retry_event(event):

    retry_count = event.get("retry_count", 0)

    if retry_count < 3:

        event["retry_count"] = retry_count + 1

        redis_client.hincrby(METRICS_KEY, "events_retried", 1)

        logger.info(f"Retrying event attempt {retry_count + 1}")

        redis_client.lpush("payment_events_retry", json.dumps(event))

    else:

        logger.error("Moving event to DLQ")

        redis_client.lpush("payment_events_dlq", json.dumps(event))

        redis_client.hincrby(METRICS_KEY, DLQ_METRIC_FIELD, 1)


# ---------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------
if __name__ == "__main__":
    start_worker()