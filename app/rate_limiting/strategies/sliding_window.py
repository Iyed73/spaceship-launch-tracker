import time
from collections.abc import Callable
from uuid import uuid4

from redis import Redis

from app.rate_limiting.rate_limit import RateLimit
from app.rate_limiting.strategies.base import RateLimitStrategy

SCRIPT = """
local key, now, period, amount, member = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3]), ARGV[4]
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - period)
if redis.call('ZCARD', key) >= amount then
    return 0
end
redis.call('ZADD', key, ARGV[1], member)
redis.call('EXPIRE', key, period)
return 1
"""


class SlidingWindowStrategy(RateLimitStrategy):
    def __init__(self, redis: Redis, clock: Callable[[], float] = time.time) -> None:
        super().__init__(redis, clock)
        self.script = redis.register_script(SCRIPT)

    def allow(self, key: str, limit: RateLimit) -> bool:
        return bool(self.script(keys=[key], args=[self.clock(), limit.period, limit.amount, uuid4().hex]))
