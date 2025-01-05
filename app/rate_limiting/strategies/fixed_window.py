from app.rate_limiting.strategies.base import RateLimitStrategy


class FixedWindowStrategy(RateLimitStrategy):
    def allow(self, key, limit):
        window = int(self.clock() // limit.period)
        pipeline = self.redis.pipeline()
        pipeline.incr(f"{key}:{window}")
        pipeline.expire(f"{key}:{window}", limit.period)
        count, _ = pipeline.execute()
        return count <= limit.amount
