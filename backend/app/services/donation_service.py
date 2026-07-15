from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.models.analytics_data import DonationLog
from app.services.action_engine import SmartInventoryActionEngine
from app.services.orphanages import match_orphanages


@dataclass(frozen=True)
class MailResult:
    status: str
    message: str


class DonationService:
    def __init__(self, db: Session, scope=None) -> None:
        self.db = db
        self.scope = scope

    def notify_orphanages(self, product_id: int) -> dict:
        suggestion = SmartInventoryActionEngine(self.db, self.scope).suggestion_for_product(product_id)
        if suggestion is None or suggestion["action"] != "DONATE":
            return {"sent": 0, "status": "skipped", "detail": "Product is not currently a donation suggestion.", "notifications": []}

        orphanages = match_orphanages(suggestion.get("store_city"))
        notifications = []
        for orphanage in orphanages:
            body = self._email_body(suggestion, orphanage)
            result = self._send_email(orphanage["email"], f"Donation available: {suggestion['product_name']}", body)
            log = DonationLog(
                realm_id=getattr(self.scope, "realm_id", None),
                store_id=suggestion.get("store_id"),
                product_id=product_id,
                orphanage_name=orphanage["name"],
                orphanage_city=orphanage["city"],
                orphanage_email=orphanage["email"],
                status=result.status,
                message=body,
            )
            self.db.add(log)
            notifications.append({**orphanage, "status": result.status, "message": result.message})

        self.db.commit()
        return {
            "sent": len(notifications),
            "status": "success",
            "detail": f"Donation request sent to {len(notifications)} orphanage(s).",
            "notifications": notifications,
        }

    def donation_history(self) -> dict:
        query = self.db.query(DonationLog)
        if self.scope is not None:
            query = query.filter(DonationLog.realm_id == self.scope.realm_id)
            if getattr(self.scope, "is_store_manager", False):
                query = query.filter(DonationLog.store_id == self.scope.assigned_store_id)
        rows = query.order_by(DonationLog.created_at.desc()).limit(50).all()
        return {
            "items": [
                {
                    "id": row.id,
                    "product_id": row.product_id,
                    "product_name": row.product.name if row.product and row.product.name else f"Product {row.product_id}",
                    "orphanage_name": row.orphanage_name,
                    "orphanage_city": row.orphanage_city,
                    "orphanage_email": row.orphanage_email,
                    "status": row.status,
                    "message": row.message,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ]
        }

    def _send_email(self, recipient: str, subject: str, body: str) -> MailResult:
        host = os.getenv("SMTP_HOST")
        username = os.getenv("SMTP_USERNAME")
        password = os.getenv("SMTP_PASSWORD")
        sender = os.getenv("SMTP_FROM", username or "donations@stocklens.local")
        port = int(os.getenv("SMTP_PORT", "587"))

        if not host or not username or not password:
            print(f"[donation-email:fallback] To: {recipient}\nSubject: {subject}\n{body}")
            return MailResult("logged", "SMTP credentials missing; email content logged for demo.")

        message = EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP(host, port, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(username, password)
                smtp.send_message(message)
            return MailResult("sent", "Email sent via SMTP.")
        except Exception as exc:
            print(f"[donation-email:error] To: {recipient}\nSubject: {subject}\n{body}\nError: {exc}")
            return MailResult("logged", f"SMTP failed; email content logged for demo: {exc}")

    def _email_body(self, suggestion: dict, orphanage: dict) -> str:
        return (
            f"Hello {orphanage['name']},\n\n"
            "StockLens has identified inventory available for donation.\n\n"
            f"Product: {suggestion['product_name']}\n"
            f"Category: {suggestion['category']}\n"
            f"Quantity available: {suggestion['current_stock_qty']}\n"
            f"Pickup location: {suggestion.get('pickup_location') or 'Warehouse'}\n\n"
            "Please let us know if you are interested in receiving this donation.\n\n"
            "Regards,\nStockLens Donation Desk"
        )
