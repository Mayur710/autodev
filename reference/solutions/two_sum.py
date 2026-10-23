"""Reference solution — human-written, used ONLY to validate the oracle tests."""


def two_sum(nums: list, target: int) -> list:
    pairs = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                # a = nums[i] appears before b = nums[j] in nums, by construction
                pairs.append([nums[i], nums[j]])
    return pairs
