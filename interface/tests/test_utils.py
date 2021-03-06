from ..compat import unwrap, wraps
from ..functional import merge
from ..utils import is_a, unique


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


def test_merge():
    assert merge([]) == {}
    assert merge([{"a": 1, "b": 2}]) == {"a": 1, "b": 2}

    result = merge([{"a": 1}, {"b": 2}, {"a": 3, "c": 4}])
    assert result == {"a": 3, "b": 2, "c": 4}
