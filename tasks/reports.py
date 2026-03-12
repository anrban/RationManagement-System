import os
import logging
from celery import Celery

logger = logging.getLogger(__name__)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL)


@celery_app.task(name="tasks.reports.generate_daily_report")
def generate_daily_report(date_str: str):
    """
    Celery task: generate a daily distribution report for the given date.
    date_str format: 'YYYY-MM-DD'
    """
    logger.info("Generating daily report for date: %s", date_str)
    # TODO: query DB, aggregate data, produce PDF/CSV report and store to S3/minio
    return {"status": "report_generated", "date": date_str}
