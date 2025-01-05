import pytest
from redis.exceptions import RedisError
from app import limiter
from app.rate_limiting.limiter import RateLimiter
from app.rate_limiting.strategies.fixed_window import FixedWindowStrategy
from app.rate_limiting.strategies.sliding_window import SlidingWindowStrategy
from app.rate_limiting.strategies.token_bucket import TokenBucketStrategy


LOGIN_DATA = {"username": "someone", "password": "12345678"}


@pytest.mark.parametrize("strategy", ("fixed_window", "sliding_window", "token_bucket"))
def test_login_fails_rate_limited(rate_limited_client, app, mocker, strategy):
    mocker.patch.object(limiter, "strategy", RateLimiter.STRATEGIES[strategy](app.redis))

    for _ in range(10):
        response = rate_limited_client.post("/authentication/login", data=LOGIN_DATA)
        assert response.status_code == 302
    response = rate_limited_client.post("/authentication/login", data=LOGIN_DATA)
    assert response.status_code == 429


def test_confirm_subscriber_fails_rate_limited(rate_limited_client):
    for _ in range(10):
        response = rate_limited_client.get("/subscription/confirm/invalid_token")
        assert response.status_code == 302
    response = rate_limited_client.get("/subscription/confirm/invalid_token")
    assert response.status_code == 429


@pytest.mark.parametrize("url", ("/launches", "/launches/past"))
def test_launches_list_fails_rate_limited(rate_limited_client, url):
    for _ in range(30):
        response = rate_limited_client.get(url)
        assert response.status_code == 200
    response = rate_limited_client.get(url)
    assert response.status_code == 429


def test_login_not_rate_limited_when_disabled(client):
    for _ in range(11):
        response = client.post("/authentication/login", data=LOGIN_DATA)
        assert response.status_code == 302


def test_login_allowed_when_storage_unavailable(rate_limited_client, mocker):
    mocker.patch.object(limiter.strategy, "allow", side_effect=RedisError)

    response = rate_limited_client.post("/authentication/login", data=LOGIN_DATA)
    assert response.status_code == 302


@pytest.mark.parametrize(("strategy", "strategy_class"),
                         (("fixed_window", FixedWindowStrategy),
                          ("sliding_window", SlidingWindowStrategy),
                          ("token_bucket", TokenBucketStrategy),))
def test_strategy_selected_from_config(app, strategy, strategy_class):
    app.config["RATE_LIMIT_STRATEGY"] = strategy
    rate_limiter = RateLimiter()
    rate_limiter.init_app(app)
    assert isinstance(rate_limiter.strategy, strategy_class)
