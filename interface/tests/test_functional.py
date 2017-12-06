from functools import total_ordering

import pytest

from ..functional import keysorted, sliding_window


def test_sliding_window():
    assert list(sliding_window([], 2)) == []
    assert list(sliding_window([1, 2, 3], 2)) == [(1, 2), (2, 3)]
    assert list(sliding_window([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]


def test_keysorted():

    @total_ordering
    class Unorderable(object):

        def __init__(self, obj):
            self.obj = obj

        def __eq__(self, other):
            raise AssertionError("Can't compare this.")

        __ne__ = __lt__ = __eq__

    with pytest.raises(AssertionError):
        sorted([Unorderable(0), Unorderable(0)])

    d = {'c': Unorderable(3), 'b': Unorderable(2), 'a': Unorderable(1)}
    items = keysorted(d)

    assert items[0][0] == 'a'
    assert items[0][1].obj == 1

    assert items[1][0] == 'b'
    assert items[1][1].obj == 2

    assert items[2][0] == 'c'
    assert items[2][1].obj == 3
