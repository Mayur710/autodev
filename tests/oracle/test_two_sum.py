from solution import two_sum


def normalize(pairs):
    """Compare pair sets order-insensitively (pair ORDER in the result list
    is not part of the spec)."""
    return sorted(tuple(sorted(p)) for p in pairs)


def test_two_sum_basic():
    assert normalize(two_sum([2, 7, 11, 15], 9)) == [(2, 7)]
    assert normalize(two_sum([3, 2, 4], 6)) == [(2, 4)]


def test_two_sum_multiple_pairs_each_once():
    got = two_sum([1, 2, 3, 4], 5)
    assert normalize(got) == [(1, 4), (2, 3)]
    assert len(got) == 2  # each pair exactly once


def test_two_sum_pair_order_follows_input():
    # spec: "with a appearing before b in nums"
    assert two_sum([5, 3, 7], 8) == [[5, 3]]


def test_two_sum_negatives():
    assert normalize(two_sum([-1, -2, -3, -4, -5], -8)) == [(-5, -3)]


def test_two_sum_no_pair_found():
    assert two_sum([1, 2, 3], 100) == []


def test_two_sum_does_not_mutate_input():
    # spec: "Do not modify nums."
    nums = [2, 7, 11, 15]
    two_sum(nums, 9)
    assert nums == [2, 7, 11, 15]
