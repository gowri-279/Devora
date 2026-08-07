def get_confidence(score: float):
    if score >= 0.85:
        return "high"
    elif score >= 0.70:
        return "medium"
    else:
        return "low"