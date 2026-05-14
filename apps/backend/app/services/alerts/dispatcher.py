from __future__ import annotations
from sqlalchemy.orm import Session
from app.db_models.alert_notification import AlertNotification
from app.db_models.alert_rule import AlertRule
from app.services.alerts.notifier import fake_notify
from app.services.alerts.rules import evaluate_rule


def dispatch_alerts(db: Session, user_id: int, event_db_id: int | None, event_payload: dict, runtime_state: dict):
    rules = db.query(AlertRule).filter(AlertRule.user_id == user_id, AlertRule.is_enabled.is_(True)).all()
    created = []
    score = event_payload.get("anomaly_score", 0)
    session_id = event_payload.get("session_id", "unknown")
    for rule in rules:
        if evaluate_rule(rule, event_payload, runtime_state):
            title = f"Anomaly alert: {rule.name}"
            message = f"Session {session_id} phát hiện bất thường với score={score:.4f}."
            notification = AlertNotification(
                rule_id=rule.id,
                user_id=user_id,
                anomaly_event_id=event_db_id,
                title=title,
                message=message,
                level="warning",
            )
            db.add(notification)
            created.append(notification)

            # Dispatch notifications based on channel
            if rule.channel == "sms" and rule.phone_number:
                fake_notify("sms", title, message, phone_number=rule.phone_number)
            else:
                fake_notify(rule.channel, title, message)

    if created:
        db.commit()
        for notification in created:
            db.refresh(notification)
    return created
