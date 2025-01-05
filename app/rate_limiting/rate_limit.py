from dataclasses import dataclass


PERIODS = {"second": 1, "minute": 60, "hour": 60 * 60, "day": 24 * 60 * 60}


@dataclass(frozen=True)
class RateLimit:
    amount: int
    period: int

    @classmethod
    def parse(cls, value):
        amount, period = value.split(" per ")
        return cls(int(amount), PERIODS[period])

    def __str__(self):
        return f"{self.amount}/{self.period}"
