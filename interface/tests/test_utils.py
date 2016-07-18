from ..utils import is_a, unique


def test_unique():
    assert list(unique(iter([1, 3, 1, 2, 3]))) == [1, 3, 2]


def test_is_a():
    assert is_a(int)(5)
    assert not is_a(str)(5)
