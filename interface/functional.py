"""
functional
----------
Functional programming utilities.
"""
from collections import deque
from operator import itemgetter
from .compat import viewkeys


def complement(f):
    def not_f(*args, **kwargs):
        return not f(*args, **kwargs)
    return not_f


def keyfilter(f, d):
    return {k: v for k, v in d.items() if f(k)}


def keysorted(d):
    return sorted(d.items(), key=itemgetter(0))


def valfilter(f, d):
    return {k: v for k, v in d.items() if f(v)}


def dzip(left, right):
    return {
        k: (left.get(k), right.get(k))
        for k in viewkeys(left) & viewkeys(right)
    }


def sliding_window(iterable, n):
    it = iter(iterable)
    items = deque(maxlen=n)
    try:
        for i in range(n):
            items.append(next(it))
    except StopIteration:
        return

    yield tuple(items)

    for item in it:
        items.append(item)
        yield tuple(items)
