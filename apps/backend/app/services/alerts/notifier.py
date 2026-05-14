from __future__ import annotations
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

def send_sms(phone_number: str, message: str) -> dict:
    """
    Send SMS notification (fake/mock mode).
    In production, replace with Twilio/Vonage/etc. implementation.
    """
    if not phone_number:
        return {"success": False, "error": "Phone number is required"}
    
    if not message:
        return {"success": False, "error": "Message is required"}
    
    if settings.SMS_ENABLED:
        logger.info("📱 SMS sent to %s | Message: %s", phone_number, message)
        return {"success": True, "provider": "fake", "to": phone_number, "message": message}
    else:
        logger.info("📱 SMS (disabled) would send to %s | Message: %s", phone_number, message)
        return {"success": True, "provider": "disabled", "to": phone_number, "message": message}

def fake_notify(channel: str, title: str, message: str, phone_number: Optional[str] = None) -> None:
    """Enhanced notifier with SMS support."""
    if channel == "sms" and phone_number:
        send_sms(phone_number, f"{title}: {message}")
    else:
        logger.info("Fake notify via %s | %s | %s", channel, title, message)
