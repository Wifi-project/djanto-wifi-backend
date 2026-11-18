from enum import StrEnum   


class WebhookEvent(StrEnum):
    PAYMENT_SUCCESS = "payment.success"
    PAYOUT_SUCCESS  = "payout.success"
    PAYOUT_FAILED   = "payout.failed"