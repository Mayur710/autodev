"""Reference solution — human-written, used ONLY to validate the oracle tests."""


def dedupe_chars(s: str) -> str:
    seen = set()
    out = []
    for ch in s:
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return "".join(out)
