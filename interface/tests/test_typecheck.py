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
    assert TypedSignature(lambda x, y, z: x).first_argument_name == 'x'
    assert TypedSignature(lambda: 0).first_argument_name is None


def test_regular_functions_arent_coroutines():

    @TypedSignature
    def foo(a, b, c):  # pragma: nocover
        pass

    assert not foo.is_coroutine

    @TypedSignature
    def bar(a, b, c):  # pragma: nocover
        yield 1

    assert not bar.is_coroutine


if PY3:  # pragma: nocover
    from ._py3_typecheck_tests import *  # noqa
