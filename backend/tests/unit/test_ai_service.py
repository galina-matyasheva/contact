from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai_service import AIService


class TestSanitizeForPrompt:
    def test_removes_angle_brackets(self) -> None:
        result = AIService._sanitize_for_prompt("<script>alert(1)</script>")
        assert "<" not in result
        assert ">" not in result

    def test_removes_curly_braces(self) -> None:
        result = AIService._sanitize_for_prompt("test {injection}")
        assert "{" not in result
        assert "}" not in result

    def test_truncates_long_input(self) -> None:
        result = AIService._sanitize_for_prompt("a" * 1000)
        assert len(result) <= 500

    def test_preserves_valid_chars(self) -> None:
        result = AIService._sanitize_for_prompt(
            "Иван Иванов +7(900)123-45-67 ivan@email.com"
        )
        assert "Иван Иванов" in result
        assert "+7(900)123-45-67" in result

    def test_strips_whitespace(self) -> None:
        result = AIService._sanitize_for_prompt("  test  ")
        assert result == "test"


class TestValidateResponse:
    def test_valid_positive(self) -> None:
        result = AIService._validate_response(
            {"sentiment": "positive", "category": "partnership", "auto_reply": "Hi!"}
        )
        assert result["sentiment"] == "positive"
        assert result["category"] == "partnership"

    def test_invalid_sentiment_becomes_unknown(self) -> None:
        result = AIService._validate_response(
            {"sentiment": "HACKED", "category": "feedback", "auto_reply": ""}
        )
        assert result["sentiment"] == "unknown"

    def test_invalid_category_becomes_other(self) -> None:
        result = AIService._validate_response(
            {"sentiment": "neutral", "category": "MALICIOUS", "auto_reply": ""}
        )
        assert result["category"] == "other"

    def test_auto_reply_truncated_if_too_long(self) -> None:
        result = AIService._validate_response(
            {"sentiment": "positive", "category": "support", "auto_reply": "x" * 1000}
        )
        assert len(result["auto_reply"]) <= 500

    def test_missing_fields_get_defaults(self) -> None:
        result = AIService._validate_response({})
        assert result["sentiment"] == "unknown"
        assert result["category"] == "other"
        assert result["auto_reply"] == ""


class TestStripMarkdownFences:
    def test_strips_json_fence(self) -> None:
        text = '```json\n{"key": "value"}\n```'
        assert AIService._strip_markdown_fences(text) == '{"key": "value"}'

    def test_strips_plain_fence(self) -> None:
        text = '```\n{"key": "value"}\n```'
        assert AIService._strip_markdown_fences(text) == '{"key": "value"}'

    def test_no_fence(self) -> None:
        text = '{"key": "value"}'
        assert AIService._strip_markdown_fences(text) == text


class TestAnalyzeContact:
    @pytest.mark.asyncio
    async def test_returns_fallback_when_no_client(self) -> None:
        svc = AIService()
        with patch.object(svc, "_get_client", new_callable=AsyncMock, return_value=None):
            result = await svc.analyze_contact(
                {"name": "Test", "email": "a@b.com", "phone": "123", "comment": "hello"}
            )
        assert result["sentiment"] == "unknown"
        assert result["category"] == "other"
        assert result["auto_reply"] == ""

    @pytest.mark.asyncio
    async def test_handles_invalid_json_from_ai(self) -> None:
        svc = AIService()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "NOT JSON"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        with patch.object(svc, "_get_client", new_callable=AsyncMock, return_value=mock_client):
            result = await svc.analyze_contact(
                {"name": "Test", "email": "a@b.com", "phone": "123", "comment": "hello"}
            )
        assert result["sentiment"] == "unknown"

    @pytest.mark.asyncio
    async def test_handles_list_response(self) -> None:
        svc = AIService()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["not", "a", "dict"]'
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        with patch.object(svc, "_get_client", new_callable=AsyncMock, return_value=mock_client):
            result = await svc.analyze_contact(
                {"name": "Test", "email": "a@b.com", "phone": "123", "comment": "hello"}
            )
        assert result["sentiment"] == "unknown"

    @pytest.mark.asyncio
    async def test_strips_markdown_fences(self) -> None:
        svc = AIService()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '```json\n{"sentiment": "positive", "category": "feedback", "auto_reply": "OK"}\n```'
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        with patch.object(svc, "_get_client", new_callable=AsyncMock, return_value=mock_client):
            result = await svc.analyze_contact(
                {"name": "Test", "email": "a@b.com", "phone": "123", "comment": "hello"}
            )
        assert result["sentiment"] == "positive"

    @pytest.mark.asyncio
    async def test_retries_on_failure(self) -> None:
        svc = AIService()
        mock_client = MagicMock()
        fail = AsyncMock(side_effect=Exception("connection error"))
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = '{"sentiment": "neutral", "category": "support", "auto_reply": "OK"}'
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[fail, Exception("timeout"), success_response]
        )
        with (
            patch.object(svc, "_get_client", new_callable=AsyncMock, return_value=mock_client),
            patch("app.services.ai_service.asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await svc.analyze_contact(
                {"name": "Test", "email": "a@b.com", "phone": "123", "comment": "hello"}
            )
        assert result["sentiment"] == "neutral"
        assert mock_client.chat.completions.create.call_count == 3

    @pytest.mark.asyncio
    async def test_returns_fallback_after_all_retries_exhausted(self) -> None:
        svc = AIService()
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("down"))
        with (
            patch.object(svc, "_get_client", new_callable=AsyncMock, return_value=mock_client),
            patch("app.services.ai_service.asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await svc.analyze_contact(
                {"name": "Test", "email": "a@b.com", "phone": "123", "comment": "hello"}
            )
        assert result["sentiment"] == "unknown"
        assert mock_client.chat.completions.create.call_count == 3
