"""Reference solution — human-written, used ONLY to validate the oracle tests."""


def max_in_list(nums: list) -> int:
    if not nums:
        raise ValueError("max_in_list() arg is an empty sequence")
    return max(nums)
