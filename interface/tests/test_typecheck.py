from ..compat import PY3
from ..typecheck import compatible
from ..typed_signature import TypedSignature


def test_compatible_when_equal():
    @TypedSignature
    def foo(a, b, c):  # pragma: nocover
        pass

    assert compatible(foo, foo)

    @TypedSignature
    def bar():  # pragma: nocover
        pass

    assert compatible(bar, bar)


def test_disallow_new_or_missing_positionals():
    @TypedSignature
    def foo(a, b):  # pragma: nocover
        pass

    @TypedSignature
    def bar(a):  # pragma: nocover
        pass

    assert not compatible(foo, bar)
    assert not compatible(bar, foo)


def test_disallow_remove_defaults():
    @TypedSignature
    def iface(a, b=3):  # pragma: nocover
        pass

    @TypedSignature
    def impl(a, b):  # pragma: nocover
        pass

    assert not compatible(impl, iface)


def test_disallow_reorder_positionals():
    @TypedSignature
    def foo(a, b):  # pragma: nocover
        pass

    @TypedSignature
    def bar(b, a):  # pragma: nocover
        pass

    assert not compatible(foo, bar)
    assert not compatible(bar, foo)


def test_allow_new_params_with_defaults_no_kwonly():
    @TypedSignature
    def iface(a, b, c):  # pragma: nocover
        pass

    @TypedSignature
    def impl(a, b, c, d=3, e=5, f=5):  # pragma: nocover
        pass

    assert compatible(impl, iface)
    assert not compatible(iface, impl)


def test_first_argument_name():
    assert TypedSignature(lambda x, y, z: x).first_argument_name == "x"
    assert TypedSignature(lambda: 0).first_argument_name is None


def test_typed_signature_repr():
    @TypedSignature
    def foo(a, b, c):  # pragma: nocover
        pass

    expected = "<TypedSignature type=function, signature=(a, b, c)>"
    assert repr(foo) == expected

    @TypedSignature
    @property
    def bar(a, b, c):  # pragma: nocover
        pass

    expected = "<TypedSignature type=property, signature=(a, b, c)>"
    assert repr(bar) == expected

    @TypedSignature
    @classmethod
    def baz(a, b, c):  # pragma: nocover
        pass

    expected = "<TypedSignature type=classmethod, signature=(a, b, c)>"
    assert repr(baz) == expected

    @TypedSignature
    @staticmethod
    def fizz(a, b, c):  # pragma: nocover
        pass

    expected = "<TypedSignature type=staticmethod, signature=(a, b, c)>"
    assert repr(fizz) == expected


if PY3:  # pragma: nocover-py2
    from ._py3_typecheck_tests import *  # noqa
