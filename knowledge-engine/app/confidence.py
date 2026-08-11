def get_confidence(score: float):
    if score >= 0.82:
        return "high"
    elif score >= 0.68:
        return "medium"
    else:
        return "low"