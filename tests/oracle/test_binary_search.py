from solution import binary_search


def test_binary_search_found():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 7) == 3
    assert binary_search(arr, 1) == 0   # first element
    assert binary_search(arr, 9) == 4   # last element


def test_binary_search_missing():
    assert binary_search([1, 2, 3], 4) == -1
    assert binary_search([1, 2, 3], 0) == -1
    assert binary_search([], 1) == -1
    assert binary_search([5], 5) == 0
    assert binary_search([5], 3) == -1


def test_binary_search_large_input():
    # guards against an accidental O(n) implementation; also bounded by
    # the executor's 15s sandbox timeout in real runs
    arr = list(range(1_000_000))
    assert binary_search(arr, 0) == 0
    assert binary_search(arr, 999_999) == 999_999
    assert binary_search(arr, 500_000) == 500_000
    assert binary_search(arr, -1) == -1
    assert binary_search(arr, 1_000_000) == -1
