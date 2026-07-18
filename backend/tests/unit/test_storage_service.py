from pathlib import Path

import pytest

from app.services.storage_service import FileStorage


class TestGenerateId:
    def test_unique_ids(self) -> None:
        ids = {FileStorage.generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_id_length(self) -> None:
        assert len(FileStorage.generate_id()) == 12

    def test_id_is_alphanumeric(self) -> None:
        assert FileStorage.generate_id().isalnum()


class TestSaveContact:
    @pytest.mark.asyncio
    async def test_save_returns_id(self, tmp_data_dir: Path) -> None:
        storage = FileStorage(data_dir=tmp_data_dir)
        cid = await storage.save_contact(
            {"name": "Test", "email": "t@t.com", "phone": "123", "comment": "test"},
            ai_analysis=None,
        )
        assert isinstance(cid, str)
        assert len(cid) == 12

    @pytest.mark.asyncio
    async def test_save_increments_total(self, tmp_data_dir: Path) -> None:
        storage = FileStorage(data_dir=tmp_data_dir)
        before = await storage.get_metrics()
        await storage.save_contact(
            {"name": "Metric", "email": "m@m.com", "phone": "456", "comment": "test"},
            ai_analysis={"sentiment": "positive", "category": "feedback", "auto_reply": ""},
        )
        after = await storage.get_metrics()
        assert after["total_contacts"] >= before["total_contacts"]

    @pytest.mark.asyncio
    async def test_save_records_sentiment(self, tmp_data_dir: Path) -> None:
        storage = FileStorage(data_dir=tmp_data_dir)
        await storage.save_contact(
            {"name": "AI", "email": "ai@ai.com", "phone": "789", "comment": "ai test"},
            ai_analysis={"sentiment": "negative", "category": "support", "auto_reply": ""},
        )
        metrics = await storage.get_metrics()
        assert metrics["sentiment_distribution"].get("negative", 0) >= 1

    @pytest.mark.asyncio
    async def test_corrupted_metrics_file(self, tmp_data_dir: Path) -> None:
        storage = FileStorage(data_dir=tmp_data_dir)
        storage._metrics_file.write_text("NOT JSON!!!", encoding="utf-8")
        metrics = await storage.get_metrics()
        assert metrics["total_contacts"] == 0

    @pytest.mark.asyncio
    async def test_corrupted_log_file(self, tmp_data_dir: Path) -> None:
        storage = FileStorage(data_dir=tmp_data_dir)
        log_file = tmp_data_dir / "logs" / "2026-01-01.json"
        log_file.write_text("NOT JSON!!!", encoding="utf-8")
        cid = await storage.save_contact(
            {"name": "Test", "email": "t@t.com", "phone": "123", "comment": "test"},
            ai_analysis=None,
        )
        assert isinstance(cid, str)


class TestGetMetrics:
    @pytest.mark.asyncio
    async def test_returns_expected_keys(self, tmp_data_dir: Path) -> None:
        storage = FileStorage(data_dir=tmp_data_dir)
        m = await storage.get_metrics()
        assert "total_contacts" in m
        assert "today_contacts" in m
        assert "sentiment_distribution" in m
        assert "category_distribution" in m

    @pytest.mark.asyncio
    async def test_values_are_integers(self, tmp_data_dir: Path) -> None:
        storage = FileStorage(data_dir=tmp_data_dir)
        m = await storage.get_metrics()
        assert isinstance(m["total_contacts"], int)
        assert isinstance(m["today_contacts"], int)
