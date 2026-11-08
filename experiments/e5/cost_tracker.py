"""Spend cap and pricing helpers for E5."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def load_pricing(path: Path | None = None) -> dict[str, dict[str, Any]]:
    path = path or (HERE / "pricing.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {m["model_id"]: m for m in data["models"]}


class SpendTracker:
    def __init__(self, max_spend_usd: float | None = None):
        env = os.environ.get("E5_MAX_SPEND_USD")
        if max_spend_usd is None:
            max_spend_usd = float(env) if env else 25.0
        self.max_spend_usd = float(max_spend_usd)
        self.spent_usd = 0.0
        self._lock = threading.Lock()
        self.events: list[dict[str, Any]] = []

    def remaining(self) -> float:
        with self._lock:
            return self.max_spend_usd - self.spent_usd

    def can_afford(self, estimate: float) -> bool:
        return estimate <= self.remaining() + 1e-12

    def charge(self, amount: float | None, meta: dict[str, Any] | None = None) -> None:
        if amount is None:
            return
        with self._lock:
            self.spent_usd += float(amount)
            self.events.append({"amount": float(amount), **(meta or {})})

    def snapshot(self) -> dict[str, float]:
        with self._lock:
            return {
                "max_spend_usd": self.max_spend_usd,
                "spent_usd": self.spent_usd,
                "remaining_usd": self.max_spend_usd - self.spent_usd,
            }


def compute_cost_usd(
    model_id: str,
    input_tokens: int | None,
    output_tokens: int | None,
    pricing: dict[str, dict[str, Any]],
    *,
    cached_tokens: int = 0,
) -> float | None:
    """Return USD cost or None if pricing unavailable for this model."""
    p = pricing.get(model_id)
    if not p:
        return None
    if p.get("input_price") is None or p.get("output_price") is None:
        return None
    if input_tokens is None or output_tokens is None:
        return None
    cached = max(0, int(cached_tokens or 0))
    billable_in = max(0, int(input_tokens) - cached)
    cost = billable_in * float(p["input_price"])
    if cached and p.get("cached_token_price") is not None:
        cost += cached * float(p["cached_token_price"])
    elif cached:
        # If cached price unknown, bill cached tokens at input price (conservative).
        cost += cached * float(p["input_price"])
    cost += int(output_tokens) * float(p["output_price"])
    return cost / 1_000_000.0
