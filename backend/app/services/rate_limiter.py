from __future__ import annotations

import asyncio
import time

from app.core.config import settings


class RateLimiter:
    """In-memory sliding window rate limiter.

    NOTE: State is per-process. With multiple uvicorn workers, each worker
    has its own limiter, effectively multiplying the allowed rate.
    Use a single worker (--workers 1) or an external store (Redis) for
    cross-process rate limiting.
    """

    def __init__(
        self,
        max_requests: int | None = None,
        window_seconds: int | None = None,
    ) -> None:
        self._max_requests = max_requests or settings.RATE_LIMIT_MAX_REQUESTS
        self._window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self._requests: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()
        self._last_cleanup: float = time.time()
        self._cleanup_interval: float = 300

    async def is_rate_limited(self, identifier: str) -> bool:
        async with self._lock:
            now = time.time()

            if now - self._last_cleanup > self._cleanup_interval:
                self._cleanup(now)

            timestamps = self._requests.get(identifier, [])
            timestamps = [t for t in timestamps if now - t < self._window_seconds]
            timestamps.append(now)
            self._requests[identifier] = timestamps

            return len(timestamps) > self._max_requests

    def _cleanup(self, now: float) -> None:
        expired = [
            key
            for key, timestamps in self._requests.items()
            if not any(now - t < self._window_seconds for t in timestamps)
        ]
        for key in expired:
            del self._requests[key]
        self._last_cleanup = now

    async def clear(self) -> None:
        """Reset all rate limit state. Test-only — not for production use."""
        async with self._lock:
            self._requests.clear()
