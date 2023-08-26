def _min(a, b):
    return a if a < b else b


def _max(a, b):
    return a if a > b else b


def clamp(val, min_v, max_v):
    return max(min_v, min(max_v, val))
