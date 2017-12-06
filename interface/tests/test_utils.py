from ..utils import is_a, unique

from ..compat import wraps, unwrap


def test_unique():
    assert list(unique(iter([1, 3, 1, 2, 3]))) == [1, 3, 2]


def test_is_a():
    assert is_a(int)(5)
    assert not is_a(str)(5)


def test_wrap_and_unwrap():
    def f(a, b, c):  # pragma: nocover
        pass

    @wraps(f)
    def g(*args):  # pragma: nocover
        pass

    assert unwrap(g) is f
