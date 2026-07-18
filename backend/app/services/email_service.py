from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from pathlib import Path

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_BASE_DELAY = 1.0
SMTP_TIMEOUT = 10.0
FILE_RETENTION_DAYS = 30
CLEANUP_INTERVAL = 86400

OWNER_SUBJECT = "Новое обращение с лендинга"
USER_SUBJECT = "Ваше обращение принято"

OWNER_BODY_TEMPLATE = """\
<h2>Новое обращение с формы обратной связи</h2>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
  <tr><td><b>Имя</b></td><td>{name}</td></tr>
  <tr><td><b>Email</b></td><td>{email}</td></tr>
  <tr><td><b>Телефон</b></td><td>{phone}</td></tr>
  <tr><td><b>Комментарий</b></td><td>{comment}</td></tr>
</table>
{ai_section}
<br><small>ID обращения: {contact_id} | Время: {timestamp}</small>
"""

USER_BODY_TEMPLATE = """\
<h2>Спасибо за обращение!</h2>
<p>Здравствуйте, {name}!</p>
<p>Мы получили ваше сообщение и свяжемся с вами в ближайшее время.</p>
{auto_reply_section}
<br><small>ID обращения: {contact_id}</small>
"""


class EmailService:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or settings.DATA_DIR
        self._emails_dir = self._data_dir / "emails"
        self._emails_dir.mkdir(parents=True, exist_ok=True)
        self._from_name = settings.SMTP_FROM_NAME or "Portfolio API"
        self._last_cleanup: float = 0.0

    def _build_ai_section(self, ai_analysis: dict | None) -> str:
        if not ai_analysis:
            return ""
        sentiment = escape(ai_analysis.get("sentiment", "—"))
        category = escape(ai_analysis.get("category", "—"))
        return (
            '<h3>AI-анализ:</h3><ul>'
            f"<li>Тональность: <b>{sentiment}</b></li>"
            f"<li>Категория: <b>{category}</b></li>"
            "</ul>"
        )

    def _build_auto_reply_section(self, ai_analysis: dict | None) -> str:
        if not ai_analysis:
            return ""
        auto_reply = ai_analysis.get("auto_reply", "")
        if not auto_reply:
            return ""
        return (
            '<h3>Рекомендуемый ответ:</h3>'
            f'<p style="color: #555; font-style: italic;">{escape(auto_reply)}</p>'
        )

    def _cleanup_old_files(self) -> None:
        cutoff = time.time() - (FILE_RETENTION_DAYS * 86400)
        for filepath in self._emails_dir.glob("*.html"):
            try:
                if filepath.stat().st_mtime < cutoff:
                    filepath.unlink()
                    logger.debug("Removed old email file: %s", filepath.name)
            except OSError as e:
                logger.warning("Failed to remove %s: %s", filepath.name, e)
        self._last_cleanup = time.time()

    def _maybe_cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup > CLEANUP_INTERVAL:
            self._cleanup_old_files()

    def _save_email_to_file(self, to_email: str, subject: str, html_body: str) -> str:
        uid = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)
        filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{uid}.html"
        filepath = self._emails_dir / filename

        full_html = (
            "<!DOCTYPE html>\n<html>\n"
            f'<head><meta charset="utf-8"><title>{escape(subject)}</title></head>\n'
            '<body style="font-family: Arial, sans-serif; padding: 20px;">\n'
            '  <div style="background: #f0f0f0; padding: 10px; margin-bottom: 20px; border-radius: 4px;">\n'
            f"    <b>To:</b> {escape(to_email)}<br>\n"
            f"    <b>Subject:</b> {escape(subject)}<br>\n"
            f"    <b>Date:</b> {escape(now.isoformat())}\n"
            "  </div>\n"
            "  <hr>\n"
            f"  {html_body}\n"
            "</body>\n</html>"
        )

        filepath.write_text(full_html, encoding="utf-8")
        logger.info("Email saved to file: %s", filepath)
        return str(filepath)

    async def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP not configured — email saved to file")
            self._save_email_to_file(to_email, subject, html_body)
            return False

        from_header = f"{self._from_name} <{settings.SMTP_USER}>"

        msg = MIMEMultipart("alternative")
        msg["From"] = from_header
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        use_tls = settings.SMTP_PORT == 465
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                await aiosmtplib.send(
                    msg,
                    hostname=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    username=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    use_tls=use_tls,
                    timeout=SMTP_TIMEOUT,
                )
                logger.info("Email sent: %s -> %s", subject, to_email)
                return True
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "SMTP failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        delay,
                        type(e).__name__,
                    )
                    await asyncio.sleep(delay)

        logger.warning("SMTP failed after %d retries (%s) — email saved to file", MAX_RETRIES + 1, type(last_error).__name__)
        self._save_email_to_file(to_email, subject, html_body)
        return False

    async def send_owner_notification(
        self,
        contact_data: dict,
        contact_id: str,
        ai_analysis: dict | None = None,
    ) -> bool:
        html = OWNER_BODY_TEMPLATE.format(
            name=escape(contact_data["name"]),
            email=escape(contact_data["email"]),
            phone=escape(contact_data["phone"]),
            comment=escape(contact_data["comment"]),
            ai_section=self._build_ai_section(ai_analysis),
            contact_id=escape(contact_id),
            timestamp=escape(contact_data.get("timestamp", "")),
        )
        recipient = settings.EMAIL_RECIPIENT or contact_data["email"]
        return await self._send_email(recipient, OWNER_SUBJECT, html)

    async def send_user_copy(
        self,
        contact_data: dict,
        contact_id: str,
        ai_analysis: dict | None = None,
    ) -> bool:
        html = USER_BODY_TEMPLATE.format(
            name=escape(contact_data["name"]),
            auto_reply_section=self._build_auto_reply_section(ai_analysis),
            contact_id=escape(contact_id),
        )
        return await self._send_email(contact_data["email"], USER_SUBJECT, html)

    async def send_emails(
        self,
        contact_data: dict,
        contact_id: str,
        ai_analysis: dict | None = None,
    ) -> dict[str, bool]:
        data = contact_data.copy()
        data["timestamp"] = data.get("timestamp", "")

        self._maybe_cleanup()

        owner_sent, user_sent = await asyncio.gather(
            self.send_owner_notification(data, contact_id, ai_analysis),
            self.send_user_copy(data, contact_id, ai_analysis),
        )
        return {"owner": owner_sent, "user_copy": user_sent}
