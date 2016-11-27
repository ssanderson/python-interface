import sys
from itertools import repeat

version_info = sys.version_info

PY2 = version_info.major == 2
PY3 = version_info.major == 3

if PY2:  # pragma: nocover
    from funcsigs import signature, Parameter

    def raise_from(e, from_):
        raise e

    def viewkeys(d):
        return d.viewkeys()

else:  # pragma: nocover
    from inspect import signature, Parameter
    exec("def raise_from(e, from_):"  # pragma: nocover
         "    raise e from from_")

    def viewkeys(d):
        return d.keys()


def zip_longest(left, right):
    """Simple zip_longest that only supports two iterators and None default.
    """
    left = iter(left)
    right = iter(right)
    left_done = False
    right_done = False
    while True:
        try:
            left_yielded = next(left)
        except StopIteration:
            left_done = True
            left_yielded = None
            left = repeat(None)
        try:
            right_yielded = next(right)
        except StopIteration:
            right_done = True
            right_yielded = None
            right = repeat(None)

        if left_done and right_done:
            raise StopIteration()

        yield left_yielded, right_yielded


# Taken from six version 1.10.0.
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
