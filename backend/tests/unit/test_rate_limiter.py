import time

import pytest

from app.services.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_under_limit_not_blocked() -> None:
    rl = RateLimiter(max_requests=5, window_seconds=60)
    for _ in range(5):
        assert await rl.is_rate_limited("ip-1") is False


@pytest.mark.asyncio
async def test_over_limit_blocked() -> None:
    rl = RateLimiter(max_requests=5, window_seconds=60)
    for _ in range(5):
        await rl.is_rate_limited("ip-2")
    assert await rl.is_rate_limited("ip-2") is True


@pytest.mark.asyncio
async def test_different_ips_independent() -> None:
    rl = RateLimiter(max_requests=5, window_seconds=60)
    for _ in range(5):
        await rl.is_rate_limited("ip-a")
    assert await rl.is_rate_limited("ip-a") is True
    assert await rl.is_rate_limited("ip-b") is False


@pytest.mark.asyncio
async def test_old_entries_cleaned_up() -> None:
    rl = RateLimiter(max_requests=5, window_seconds=60)
    rl._requests["stale-ip"] = [time.time() - 120]
    await rl.is_rate_limited("stale-ip")
    assert "stale-ip" in rl._requests
    assert len(rl._requests["stale-ip"]) == 1


@pytest.mark.asyncio
async def test_clear_resets_state() -> None:
    rl = RateLimiter(max_requests=2, window_seconds=60)
    await rl.is_rate_limited("x")
    await rl.is_rate_limited("x")
    assert await rl.is_rate_limited("x") is True
    await rl.clear()
    assert await rl.is_rate_limited("x") is False
