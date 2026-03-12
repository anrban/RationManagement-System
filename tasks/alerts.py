import os
import logging
from celery import Celery

logger = logging.getLogger(__name__)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL)


@celery_app.task(name="tasks.alerts.send_fraud_alert")
def send_fraud_alert(beneficiary_id: str):
    """
    Celery task: send a fraud alert notification for the given beneficiary.
    Triggered when a beneficiary is flagged for fraud or duplication.
    """
    logger.info("Sending fraud alert for beneficiary: %s", beneficiary_id)
    # TODO: integrate with email / SMS alerting service
    return {"status": "alert_sent", "beneficiary_id": beneficiary_id}
