# ---------------------------------------------------
# EVENT PUBLISHER (REDIS)
# ---------------------------------------------------

# Redis client for event queue
import redis

# JSON for serialization
import json


class EventPublisher:
    """
    Publishes events to Redis queue.

    Used by:
    - PaymentService (producer)
    - Worker consumes these events asynchronously
    """

    def __init__(self):
        # Initialize Redis connection
        self.redis_client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True
        )

        # Queue name (single source of truth)
        self.queue_name = "payment_events"

    # ---------------------------------------------------
    # PUBLISH EVENT
    # ---------------------------------------------------
    def publish(self, event: dict):
        """
        Publishes an event to Redis queue.

        Args:
            event (dict): event payload
        """

        try:
            # Convert event to JSON string
            event_json = json.dumps(event)

            # Push event into Redis queue
            self.redis_client.lpush(self.queue_name, event_json)

            # Debug log
            print(f"[EVENT PUBLISHED] → {event['event_type']} | txn={event['payload'].get('transaction_id')}")

        except Exception as e:
            # Fail-safe logging (do NOT crash API)
            print("[ERROR] Failed to publish event:", str(e))