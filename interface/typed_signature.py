"""
A wrapper around inspect.signature that knows what kind of type it came from.

This is useful for when we care about the distinction between different kinds
of callables, e.g., between methods, classmethods, and staticmethods.
"""
from .compat import signature


class TypedSignature(object):
    """
    Wrapper around an inspect.Signature that knows what kind of callable it came from.

    Parameters
    ----------
    obj : callable
        An object from which to extract a signature and a type.
    """
    def __init__(self, obj):
        self._type = type(obj)
        if isinstance(obj, (classmethod, staticmethod)):
            self._signature = signature(obj.__func__)
        elif isinstance(obj, property):
            self._signature = signature(obj.fget)
        else:
            self._signature = signature(obj)

    @property
    def signature(self):
        return self._signature

    @property
    def type(self):
        return self._type

    def __str__(self):
        return str(self._signature)
