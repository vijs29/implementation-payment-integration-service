# ---------------------------------------------------
# PAYMENT STATE MACHINE
# ---------------------------------------------------

# Controls valid lifecycle transitions for payment transactions

from app.models.payment_transaction import PaymentStatus


class PaymentStateMachine:
    """
    Enforces valid state transitions for payments.

    Prevents:
    - Invalid lifecycle jumps
    - Data inconsistency
    - Broken workflows
    """

    # ---------------------------------------------------
    # ALLOWED TRANSITIONS
    # ---------------------------------------------------
    allowed_transitions = {

        # Initial state
        PaymentStatus.CREATED: [
            PaymentStatus.PROCESSING,
            PaymentStatus.FAILED
        ],

        # Worker has picked up the payment
        PaymentStatus.PROCESSING: [
            PaymentStatus.AUTHORIZED,
            PaymentStatus.FAILED
        ],

        # Payment authorized by processor
        PaymentStatus.AUTHORIZED: [
            PaymentStatus.SETTLED,
            PaymentStatus.FAILED
        ],

        # Final successful settlement
        PaymentStatus.SETTLED: [
            PaymentStatus.REFUNDED
        ],

        # Terminal states
        PaymentStatus.FAILED: [],
        PaymentStatus.REFUNDED: []
    }

    # ---------------------------------------------------
    # VALIDATE TRANSITION
    # ---------------------------------------------------
    @classmethod
    def validate_transition(
        cls,
        current_status: PaymentStatus,
        new_status: PaymentStatus
    ) -> bool:
        """
        Validates if a transition is allowed.

        - Allows idempotent transitions (same state → same state)
        - Prevents invalid lifecycle jumps

        Raises:
            ValueError if invalid transition
        """

        # ------------------------------------------
        # IDENTITY / IDEMPOTENCY CHECK
        # ------------------------------------------
        if current_status == new_status:
            return True

        # ------------------------------------------
        # VALID TRANSITION CHECK
        # ------------------------------------------
        allowed = cls.allowed_transitions.get(current_status, [])

        if new_status not in allowed:
            raise ValueError(
                f"Invalid payment state transition: {current_status} -> {new_status}"
            )

        return True