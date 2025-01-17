from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import Flask, abort, current_app, request
from redis.exceptions import RedisError

from app.rate_limiting.rate_limit import RateLimit
from app.rate_limiting.strategies.base import RateLimitStrategy
from app.rate_limiting.strategies.fixed_window import FixedWindowStrategy
from app.rate_limiting.strategies.sliding_window import SlidingWindowStrategy
from app.rate_limiting.strategies.token_bucket import TokenBucketStrategy

P = ParamSpec("P")
R = TypeVar("R")


class RateLimiter:
    STRATEGIES: dict[str, type[RateLimitStrategy]] = {
        "fixed_window": FixedWindowStrategy,
        "sliding_window": SlidingWindowStrategy,
        "token_bucket": TokenBucketStrategy,
    }

    def __init__(self) -> None:
        self.enabled = False
        self.strategy: RateLimitStrategy | None = None
        self.default_limits: list[RateLimit] = []

    def init_app(self, app: Flask) -> None:
        self.enabled = app.config["RATE_LIMIT_ENABLED"]
        self.strategy = self.STRATEGIES[app.config["RATE_LIMIT_STRATEGY"]](app.redis)
        self.default_limits = [RateLimit.parse(limit) for limit in app.config["RATE_LIMIT_DEFAULTS"]]
        app.before_request(self.check_default_limits)

    def check_default_limits(self) -> None:
        if request.endpoint and request.endpoint != "static":
            self.check(request.endpoint, self.default_limits)

    def limit(self, *limits: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
        parsed_limits = [RateLimit.parse(limit) for limit in limits]

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
                self.check(f"{func.__module__}.{func.__qualname__}", parsed_limits)
                return func(*args, **kwargs)

            return decorated_function

        return decorator

    def check(self, scope: str, limits: list[RateLimit]) -> None:
        if not self.enabled:
            return
        for limit in limits:
            if not self.allow(f"rate_limit:{scope}:{request.remote_addr}:{limit}", limit):
                abort(429)

    def allow(self, key: str, limit: RateLimit) -> bool:
        try:
            return self.strategy.allow(key, limit)
        except RedisError:
            current_app.logger.exception("Rate limit storage is unavailable")
            return True
