from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock


class SlidingWindowLimiter:
    """In-memory sliding window rate limiter.

    Tracks request timestamps per key within a rolling window and rejects
    requests that exceed the configured maximum.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str, max_requests: int | None = None) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        limit = max_requests if max_requests is not None else self.max_requests

        with self._lock:
            timestamps = [t for t in self._timestamps[key] if t > cutoff]
            self._timestamps[key] = timestamps

            if len(timestamps) >= limit:
                return False

            timestamps.append(now)
            return True

    def cleanup(self) -> None:
        """Remove keys with no recent activity to prevent memory growth."""
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            empty_keys = [
                k
                for k, ts in self._timestamps.items()
                if not ts or max(ts) <= cutoff
            ]
            for k in empty_keys:
                del self._timestamps[k]


# Per-API-key burst limiter (e.g., 10 req/sec)
_burst_limiter: SlidingWindowLimiter | None = None

# Per-IP limiter for all requests (e.g., 60 req/min)
_ip_limiter: SlidingWindowLimiter | None = None


def get_burst_limiter() -> SlidingWindowLimiter:
    global _burst_limiter
    if _burst_limiter is None:
        from gnosis_api.config import settings

        _burst_limiter = SlidingWindowLimiter(
            max_requests=settings.rate_limit_burst,
            window_seconds=settings.rate_limit_burst_window,
        )
    return _burst_limiter


def get_ip_limiter() -> SlidingWindowLimiter:
    global _ip_limiter
    if _ip_limiter is None:
        from gnosis_api.config import settings

        _ip_limiter = SlidingWindowLimiter(
            max_requests=settings.rate_limit_ip,
            window_seconds=settings.rate_limit_ip_window,
        )
    return _ip_limiter


def cleanup_limiters() -> None:
    if _burst_limiter is not None:
        _burst_limiter.cleanup()
    if _ip_limiter is not None:
        _ip_limiter.cleanup()
