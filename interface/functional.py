"""
functional
----------
Functional programming utilities.
"""
from .compat import viewkeys


def complement(f):
    def not_f(*args, **kwargs):
        return not f(*args, **kwargs)
    return not_f


def keyfilter(f, d):
    return {k: v for k, v in d.items() if f(k)}


def valfilter(f, d):
    return {k: v for k, v in d.items() if f(v)}


def dzip(left, right):
    return {
        k: (left.get(k), right.get(k))
        for k in viewkeys(left) & viewkeys(right)
    }
