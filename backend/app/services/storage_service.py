from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class FileStorage:
    RETENTION_DAYS = 30

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or settings.DATA_DIR
        (self._data_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self._data_dir / "metrics").mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._last_cleanup: float = 0.0

    @property
    def _metrics_file(self) -> Path:
        return self._data_dir / "metrics.json"

    def _cleanup_old_logs(self) -> None:
        now = time.time()
        if now - self._last_cleanup < 86400:
            return
        self._last_cleanup = now
        cutoff = now - (self.RETENTION_DAYS * 86400)
        logs_dir = self._data_dir / "logs"
        for filepath in logs_dir.glob("*.jsonl"):
            try:
                if filepath.stat().st_mtime < cutoff:
                    filepath.unlink()
                    logger.debug("Removed old log file: %s", filepath.name)
            except OSError as e:
                logger.warning("Failed to remove %s: %s", filepath.name, e)

    def _load_metrics_sync(self) -> dict:
        default = {
            "total_contacts": 0,
            "today_contacts": 0,
            "today_date": "",
            "sentiment_distribution": {},
            "category_distribution": {},
        }
        if not self._metrics_file.exists():
            return default
        try:
            data = json.loads(self._metrics_file.read_text(encoding="utf-8"))
            data.pop("contacts", None)
            return data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load metrics, using defaults: %s", e)
            return default

    def _save_metrics_sync(self, data: dict) -> None:
        data.pop("contacts", None)
        tmp = self._metrics_file.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            os.replace(str(tmp), str(self._metrics_file))
        except OSError as e:
            logger.error("Failed to save metrics: %s", e)
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    @staticmethod
    def generate_id() -> str:
        return uuid.uuid4().hex[:12]

    async def save_contact(
        self,
        contact_data: dict,
        ai_analysis: dict | None = None,
    ) -> str:
        async with self._lock:
            return await asyncio.to_thread(
                self._save_contact_sync, contact_data, ai_analysis
            )

    def _save_contact_sync(
        self,
        contact_data: dict,
        ai_analysis: dict | None = None,
    ) -> str:
        self._cleanup_old_logs()
        contact_id = self.generate_id()
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")

        metrics = self._load_metrics_sync()

        if metrics.get("today_date") != today_str:
            metrics["today_contacts"] = 0
            metrics["today_date"] = today_str

        metrics["total_contacts"] += 1
        metrics["today_contacts"] += 1

        if ai_analysis:
            sentiment = ai_analysis.get("sentiment", "unknown")
            category = ai_analysis.get("category", "other")
            metrics["sentiment_distribution"][sentiment] = (
                metrics["sentiment_distribution"].get(sentiment, 0) + 1
            )
            metrics["category_distribution"][category] = (
                metrics["category_distribution"].get(category, 0) + 1
            )

        self._save_metrics_sync(metrics)

        entry = {
            "id": contact_id,
            "name": contact_data.get("name", ""),
            "email": contact_data.get("email", ""),
            "phone": contact_data.get("phone", ""),
            "comment": contact_data.get("comment", ""),
            "ai_analysis": ai_analysis,
            "timestamp": now.isoformat(),
        }

        log_file = self._data_dir / "logs" / f"{today_str}.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.error("Failed to write log file %s: %s", log_file, e)

        logger.info("Contact %s saved", contact_id)
        return contact_id

    async def get_metrics(self) -> dict:
        async with self._lock:
            return await asyncio.to_thread(self._get_metrics_sync)

    def _get_metrics_sync(self) -> dict:
        metrics = self._load_metrics_sync()
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")

        if metrics.get("today_date") != today_str:
            metrics["today_contacts"] = 0

        return {
            "total_contacts": metrics.get("total_contacts", 0),
            "today_contacts": metrics.get("today_contacts", 0),
            "sentiment_distribution": metrics.get("sentiment_distribution", {}),
            "category_distribution": metrics.get("category_distribution", {}),
        }
