"""
Miscellaneous utilities.
"""


def unique(g):
    """
    Yield values yielded by ``g``, removing any duplicates.

    Example
    -------
    >>> list(unique(iter([1, 3, 1, 2, 3])))
    [1, 3, 2]
    """
    yielded = set()
    for value in g:
        if value not in yielded:
            yield value
            yielded.add(value)


def is_a(t):
    """
    Partially-applied, flipped isinstance.

    >>> is_a(int)(5)
    True
    >>> is_a(str)(5)
    False
    """
    return lambda v: isinstance(v, t)
