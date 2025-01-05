import time
from abc import ABC, abstractmethod


class RateLimitStrategy(ABC):
    def __init__(self, redis, clock=time.time):
        self.redis = redis
        self.clock = clock

    @abstractmethod
    def allow(self, key, limit):
        pass
