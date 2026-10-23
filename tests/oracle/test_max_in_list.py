import pytest
from solution import max_in_list


@pytest.mark.parametrize("nums,expected", [
    ([1, 2, 3], 3),
    ([-5, -1, -9], -1),
    ([7], 7),
    ([3, 3, 3], 3),
    ([1.5, 2.5, 0.5], 2.5),
])
def test_max_in_list_nominal(nums, expected):
    assert max_in_list(nums) == expected


def test_max_in_list_empty_raises():
    with pytest.raises(ValueError):
        max_in_list([])
