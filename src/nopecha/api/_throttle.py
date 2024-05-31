"""
Throttler for API calls with exponential backoff.
Will automatically sleep for you.

Usage:

for _ in sleeper(throttle()):
    pass # call the API


async for _ in async_sleeper(throttle()):
    pass # call the API

"""

import asyncio
import time
import typing


def linear_throttle(*, factor: float = 1, max_sleep: float = 60, max_attempts: int = 0):
    yield 0  # first one is free
    attempt = 0
    while max_attempts > attempt or max_attempts <= 0:
        attempt += 1
        yield min(factor * attempt, max_sleep)


def exp_throttle(*, base: float = 1.54, max_sleep: float = 60, max_attempts: int = 0):
    yield 0  # first one is free
    attempt = 0
    while max_attempts > attempt or max_attempts < 0:
        attempt += 1
        yield min(base**attempt, max_sleep)


def sleeper(gen: typing.Generator[float, None, None]):
    for delay in gen:
        yield time.sleep(delay)


async def async_sleeper(gen: typing.Generator[float, None, None]):
    for delay in gen:
        yield await asyncio.sleep(delay)
