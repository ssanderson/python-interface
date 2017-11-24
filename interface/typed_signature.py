"""
A wrapper around inspect.signature that knows what kind of type it came from.

This is useful for when we care about the distinction between different kinds
of callables, e.g., between methods, classmethods, and staticmethods.
"""
import types

from .compat import signature
from .default import default


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
        self._signature = signature(extract_func(obj))

    @property
    def signature(self):
        return self._signature

    @property
    def first_argument_name(self):
        try:
            return next(iter(self.signature.parameters))
        except StopIteration:
            return None

    @property
    def type(self):
        return self._type

    def __str__(self):
        return str(self._signature)


BUILTIN_FUNCTION_TYPES = (types.FunctionType, types.BuiltinFunctionType)


def extract_func(obj):
    if isinstance(obj, BUILTIN_FUNCTION_TYPES):
        # Fast path, since this is the most likely case.
        return obj
    elif isinstance(obj, (classmethod, staticmethod)):
        return obj.__func__
    elif isinstance(obj, property):
        return obj.fget
    elif isinstance(obj, default):
        return extract_func(obj.implementation)
    else:
        return obj
