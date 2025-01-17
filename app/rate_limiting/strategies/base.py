import time
from abc import ABC, abstractmethod
from collections.abc import Callable

from redis import Redis

from app.rate_limiting.rate_limit import RateLimit


class RateLimitStrategy(ABC):
    def __init__(self, redis: Redis, clock: Callable[[], float] = time.time) -> None:
        self.redis = redis
        self.clock = clock

    @abstractmethod
    def allow(self, key: str, limit: RateLimit) -> bool:
        pass
