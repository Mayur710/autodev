from solution import flatten


def test_flatten_basic():
    assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]


def test_flatten_deeply_nested():
    assert flatten([1, [2, [3, [4, [5]]]]]) == [1, 2, 3, 4, 5]


def test_flatten_empty_inputs():
    assert flatten([]) == []
    assert flatten([[], [[]], [[[]]]]) == []


def test_flatten_mixed_with_inner_empties():
    assert flatten([1, [[], 2], [3]]) == [1, 2, 3]


def test_flatten_does_not_mutate_input():
    lst = [1, [2, [3]]]
    flatten(lst)
    assert lst == [1, [2, [3]]]
