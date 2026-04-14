def pct_diff(low: float, high: float) -> float:
    if low <= 0:
        return 0.0
    return ((high - low) / low) * 100
