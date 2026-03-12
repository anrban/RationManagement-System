import os
import random
import logging

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def send_sms_otp(phone_number: str, otp: str) -> bool:
    """
    Send an SMS OTP to the beneficiary phone number via Twilio.
    Returns True on success, False on failure.
    This is a stub — configure Twilio credentials via environment variables.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials not configured. SMS not sent.")
        return False

    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your OTP for Digital Ration System: {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number,
        )
        logger.info("SMS sent: %s", message.sid)
        return True
    except Exception as exc:
        logger.error("Failed to send SMS: %s", exc)
        return False


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP of the given length."""
    return "".join([str(random.randint(0, 9)) for _ in range(length)])
