from unittest.mock import AsyncMock, patch

import pytest

from app.services.email_service import EmailService


class TestHtmlEscaping:
    @pytest.mark.asyncio
    async def test_owner_template_escapes_script_in_name(self) -> None:
        svc = EmailService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock, return_value=True) as mock:
            await svc.send_owner_notification(
                {
                    "name": "<script>alert('xss')</script>",
                    "email": "a@b.com",
                    "phone": "123",
                    "comment": "test",
                },
                "id1",
            )
            html = mock.call_args[0][2]
            assert "<script>" not in html
            assert "&lt;script&gt;" in html

    @pytest.mark.asyncio
    async def test_owner_template_escapes_script_in_comment(self) -> None:
        svc = EmailService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock, return_value=True) as mock:
            await svc.send_owner_notification(
                {
                    "name": "Normal",
                    "email": "a@b.com",
                    "phone": "123",
                    "comment": "<img onerror=alert(1)>",
                },
                "id2",
            )
            html = mock.call_args[0][2]
            assert "<img" not in html
            assert "&lt;img" in html

    @pytest.mark.asyncio
    async def test_user_template_escapes_html_in_name(self) -> None:
        svc = EmailService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock, return_value=True) as mock:
            await svc.send_user_copy(
                {
                    "name": "<b>bold</b>",
                    "email": "a@b.com",
                    "phone": "123",
                    "comment": "test",
                },
                "id3",
            )
            html = mock.call_args[0][2]
            assert "<b>bold</b>" not in html
            assert "&lt;b&gt;bold&lt;/b&gt;" in html

    def test_ai_section_escapes_values(self) -> None:
        svc = EmailService()
        ai = {"sentiment": "<script>x</script>", "category": "test", "auto_reply": ""}
        html = svc._build_ai_section(ai)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_auto_reply_section_escapes_output(self) -> None:
        svc = EmailService()
        ai = {"auto_reply": "<img src=x onerror=alert(1)>"}
        html = svc._build_auto_reply_section(ai)
        assert "<img" not in html
        assert "&lt;img" in html


class TestSaveEmailToFile:
    def test_creates_html_file(self, tmp_path) -> None:
        svc = EmailService(data_dir=tmp_path)
        path = svc._save_email_to_file("test@example.com", "Test Subject", "<p>Hello</p>")
        assert path.endswith(".html")
        import os

        assert os.path.exists(path)
        content = open(path, encoding="utf-8").read()
        assert "test@example.com" in content
        assert "Test Subject" in content
        assert "<p>Hello</p>" in content


class TestCleanupOldFiles:
    def test_removes_old_files(self, tmp_path) -> None:
        emails_dir = tmp_path / "emails"
        emails_dir.mkdir()
        old_file = emails_dir / "20200101_000000_abc12345.html"
        old_file.write_text("<p>old</p>")
        import os
        os.utime(old_file, (0, 0))

        svc = EmailService(data_dir=tmp_path)
        svc._cleanup_old_files()
        assert not old_file.exists()

    def test_keeps_recent_files(self, tmp_path) -> None:
        emails_dir = tmp_path / "emails"
        emails_dir.mkdir()
        recent_file = emails_dir / "recent.html"
        recent_file.write_text("<p>recent</p>")

        svc = EmailService(data_dir=tmp_path)
        svc._cleanup_old_files()
        assert recent_file.exists()
