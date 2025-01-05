from app.rate_limiting.strategies.base import RateLimitStrategy


SCRIPT = """
local key, now, period, amount = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3])
local bucket = redis.call('HMGET', key, 'tokens', 'refilled_at')
local tokens = tonumber(bucket[1]) or amount
local refilled_at = tonumber(bucket[2]) or now
tokens = math.min(amount, tokens + (now - refilled_at) * amount / period)
local allowed = tokens >= 1
if allowed then
    tokens = tokens - 1
end
redis.call('HSET', key, 'tokens', tokens, 'refilled_at', ARGV[1])
redis.call('EXPIRE', key, period)
return allowed and 1 or 0
"""


class TokenBucketStrategy(RateLimitStrategy):
    def __init__(self, redis, **kwargs):
        super().__init__(redis, **kwargs)
        self.script = redis.register_script(SCRIPT)

    def allow(self, key, limit):
        return bool(self.script(keys=[key], args=[self.clock(), limit.period, limit.amount]))
