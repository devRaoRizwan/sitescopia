from collections import defaultdict, deque
from math import ceil
from time import monotonic


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int, max_keys: int = 10000) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> tuple[bool, int]:
        if self.limit <= 0:
            return True, 0

        now = monotonic()
        requests = self._requests.get(key)
        if requests is None:
            if len(self._requests) >= self.max_keys:
                cutoff = now - self.window_seconds
                for existing_key, existing_requests in list(self._requests.items()):
                    while existing_requests and existing_requests[0] <= cutoff:
                        existing_requests.popleft()
                    if not existing_requests:
                        self._requests.pop(existing_key, None)
                
            if len(self._requests) >= self.max_keys:
                key = "__rate_limit_overflow__"
                requests = self._requests[key]
            else:
                requests = deque()
                self._requests[key] = requests
        cutoff = now - self.window_seconds

        while requests and requests[0] <= cutoff:
            requests.popleft()

        if len(requests) >= self.limit:
            retry_after = max(1, ceil(self.window_seconds - (now - requests[0])))
            return False, retry_after

        requests.append(now)
        return True, 0