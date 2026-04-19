"""Sampling utilities for logslice: reservoir and rate-based sampling."""

import random
from typing import Iterable, Iterator


def reservoir_sample(records: Iterable[dict], n: int, seed: int = None) -> list:
    """Return up to n records chosen uniformly at random (reservoir sampling)."""
    rng = random.Random(seed)
    reservoir = []
    for i, record in enumerate(records):
        if i < n:
            reservoir.append(record)
        else:
            j = rng.randint(0, i)
            if j < n:
                reservoir[j] = record
    return reservoir


def rate_sample(records: Iterable[dict], rate: float, seed: int = None) -> Iterator[dict]:
    """Yield each record with probability `rate` (0.0–1.0)."""
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"rate must be between 0.0 and 1.0, got {rate}")
    rng = random.Random(seed)
    for record in records:
        if rng.random() < rate:
            yield record


def nth_sample(records: Iterable[dict], n: int) -> Iterator[dict]:
    """Yield every nth record (1-based: n=1 keeps all, n=2 keeps every other)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    for i, record in enumerate(records):
        if i % n == 0:
            yield record
