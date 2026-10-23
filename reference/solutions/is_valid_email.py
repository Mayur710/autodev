"""Reference solution — human-written, used ONLY to validate the oracle tests.

Implements EXACTLY the stated spec: one '@', at least one '.' after the '@',
no spaces. Deliberately no stricter (no TLD whitelist, etc.)."""


def is_valid_email(s: str) -> bool:
    if " " in s:
        return False
    if s.count("@") != 1:
        return False
    local, _, domain = s.partition("@")
    return local != "" and "." in domain
