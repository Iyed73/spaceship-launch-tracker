from functools import wraps
from flask import request, abort, current_app
from redis.exceptions import RedisError
from app.rate_limiting.rate_limit import RateLimit
from app.rate_limiting.strategies.fixed_window import FixedWindowStrategy
from app.rate_limiting.strategies.sliding_window import SlidingWindowStrategy
from app.rate_limiting.strategies.token_bucket import TokenBucketStrategy


class RateLimiter:
    STRATEGIES = {
        "fixed_window": FixedWindowStrategy,
        "sliding_window": SlidingWindowStrategy,
        "token_bucket": TokenBucketStrategy,
    }

    def __init__(self):
        self.enabled = False
        self.strategy = None
        self.default_limits = []

    def init_app(self, app):
        self.enabled = app.config["RATE_LIMIT_ENABLED"]
        self.strategy = self.STRATEGIES[app.config["RATE_LIMIT_STRATEGY"]](app.redis)
        self.default_limits = [RateLimit.parse(limit) for limit in app.config["RATE_LIMIT_DEFAULTS"]]
        app.before_request(self.check_default_limits)

    def check_default_limits(self):
        if request.endpoint and request.endpoint != "static":
            self.check(request.endpoint, self.default_limits)

    def limit(self, *limits):
        limits = [RateLimit.parse(limit) for limit in limits]

        def decorator(func):
            @wraps(func)
            def decorated_function(*args, **kwargs):
                self.check(f"{func.__module__}.{func.__qualname__}", limits)
                return func(*args, **kwargs)
            return decorated_function
        return decorator

    def check(self, scope, limits):
        if not self.enabled:
            return
        for limit in limits:
            if not self.allow(f"rate_limit:{scope}:{request.remote_addr}:{limit}", limit):
                abort(429)

    def allow(self, key, limit):
        try:
            return self.strategy.allow(key, limit)
        except RedisError:
            current_app.logger.exception("Rate limit storage is unavailable")
            return True
