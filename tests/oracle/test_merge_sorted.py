from solution import merge_sorted


def test_merge_interleaved():
    assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]


def test_merge_with_empty():
    assert merge_sorted([], [1, 2]) == [1, 2]
    assert merge_sorted([1, 2], []) == [1, 2]
    assert merge_sorted([], []) == []


def test_merge_with_duplicates_and_negatives():
    assert merge_sorted([1, 1, 2], [1]) == [1, 1, 1, 2]
    assert merge_sorted([-5, -1], [-3, 0]) == [-5, -3, -1, 0]


def test_merge_does_not_mutate_inputs():
    # spec: "Do not modify the input lists."
    a, b = [1, 3], [2, 4]
    merge_sorted(a, b)
    assert a == [1, 3] and b == [2, 4]


def test_merge_output_is_sorted_and_complete():
    a, b = [1, 4, 9, 15], [2, 3, 8]
    out = merge_sorted(a, b)
    assert out == sorted(out)
    assert len(out) == len(a) + len(b)
