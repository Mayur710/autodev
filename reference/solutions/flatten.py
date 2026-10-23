"""Reference solution — human-written, used ONLY to validate the oracle tests."""


def flatten(lst: list) -> list:
    out = []
    for item in lst:
        if isinstance(item, list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out
