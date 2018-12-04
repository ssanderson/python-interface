import functools
import sys

version_info = sys.version_info

PY2 = version_info.major == 2
PY3 = version_info.major == 3

if PY2:  # pragma: nocover-py3
    from itertools import izip_longest as zip_longest
    from funcsigs import signature, Parameter

    @functools.wraps(functools.wraps)
    def wraps(func, *args, **kwargs):
        outer_decorator = functools.wraps(func, *args, **kwargs)

        def decorator(f):
            wrapped = outer_decorator(f)
            wrapped.__wrapped__ = func
            return wrapped

        return decorator

    def raise_from(e, from_):
        raise e

    def viewkeys(d):
        return d.viewkeys()

    def unwrap(func, stop=None):
        # NOTE: implementation is taken from CPython/Lib/inspect.py, Python 3.6
        if stop is None:
            def _is_wrapper(f):
                return hasattr(f, '__wrapped__')
        else:
            def _is_wrapper(f):
                return hasattr(f, '__wrapped__') and not stop(f)
        f = func  # remember the original func for error reporting
        memo = {id(f)}  # Memoise by id to tolerate non-hashable objects
        while _is_wrapper(func):
            func = func.__wrapped__
            id_func = id(func)
            if id_func in memo:
                raise ValueError('wrapper loop when unwrapping {!r}'.format(f))
            memo.add(id_func)
        return func


else:  # pragma: nocover-py2
    from inspect import signature, Parameter, unwrap
    from itertools import zip_longest

    wraps = functools.wraps

    exec("def raise_from(e, from_):"  # pragma: nocover
         "    raise e from from_")

    def viewkeys(d):
        return d.keys()


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
