import pytest
from uuid import uuid4
from app.rate_limiting.rate_limit import RateLimit
from app.rate_limiting.strategies.fixed_window import FixedWindowStrategy
from app.rate_limiting.strategies.sliding_window import SlidingWindowStrategy
from app.rate_limiting.strategies.token_bucket import TokenBucketStrategy


STRATEGIES = (FixedWindowStrategy, SlidingWindowStrategy, TokenBucketStrategy)
LIMIT = RateLimit(amount=10, period=60)


class Clock:
    def __init__(self):
        self.now = 1200000000

    def __call__(self):
        return self.now


@pytest.fixture()
def clock():
    return Clock()


@pytest.fixture()
def key():
    return f"test_rate_limit:{uuid4().hex}"


@pytest.mark.parametrize(("value", "limit"),
                         (("10 per minute", RateLimit(10, 60)),
                          ("100 per hour", RateLimit(100, 3600)),
                          ("500 per day", RateLimit(500, 86400)),))
def test_rate_limit_parse(value, limit):
    assert RateLimit.parse(value) == limit


@pytest.mark.parametrize("strategy_class", STRATEGIES)
def test_strategy_allows_up_to_limit(app, clock, key, strategy_class):
    strategy = strategy_class(app.redis, clock=clock)
    assert all(strategy.allow(key, LIMIT) for _ in range(10))
    assert not strategy.allow(key, LIMIT)


@pytest.mark.parametrize("strategy_class", STRATEGIES)
def test_strategy_allows_again_after_period(app, clock, key, strategy_class):
    strategy = strategy_class(app.redis, clock=clock)
    assert all(strategy.allow(key, LIMIT) for _ in range(10))
    clock.now += 60
    assert all(strategy.allow(key, LIMIT) for _ in range(10))
    assert not strategy.allow(key, LIMIT)


@pytest.mark.parametrize("strategy_class", STRATEGIES)
def test_strategy_limits_each_key_separately(app, clock, key, strategy_class):
    strategy = strategy_class(app.redis, clock=clock)
    assert all(strategy.allow(key, LIMIT) for _ in range(10))
    assert strategy.allow(f"{key}:other", LIMIT)


def test_fixed_window_allows_burst_at_window_boundary(app, clock, key):
    strategy = FixedWindowStrategy(app.redis, clock=clock)
    clock.now += 59
    assert all(strategy.allow(key, LIMIT) for _ in range(10))
    clock.now += 1
    assert all(strategy.allow(key, LIMIT) for _ in range(10))


@pytest.mark.parametrize("strategy_class", (SlidingWindowStrategy, TokenBucketStrategy))
def test_strategy_rejects_burst_at_window_boundary(app, clock, key, strategy_class):
    strategy = strategy_class(app.redis, clock=clock)
    clock.now += 59
    assert all(strategy.allow(key, LIMIT) for _ in range(10))
    clock.now += 1
    assert not strategy.allow(key, LIMIT)


def test_sliding_window_allows_as_requests_leave_window(app, clock, key):
    strategy = SlidingWindowStrategy(app.redis, clock=clock)
    assert strategy.allow(key, LIMIT)
    clock.now += 30
    assert all(strategy.allow(key, LIMIT) for _ in range(9))
    clock.now += 30
    assert strategy.allow(key, LIMIT)
    assert not strategy.allow(key, LIMIT)


def test_token_bucket_refills_gradually(app, clock, key):
    strategy = TokenBucketStrategy(app.redis, clock=clock)
    assert all(strategy.allow(key, LIMIT) for _ in range(10))
    clock.now += 6
    assert strategy.allow(key, LIMIT)
    assert not strategy.allow(key, LIMIT)
