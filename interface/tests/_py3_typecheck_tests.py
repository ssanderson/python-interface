from inspect import signature

from ..typecheck import compatible


def test_allow_new_params_with_defaults_with_kwonly():

    @signature
    def iface(a, b, c):  # pragma: nocover
        pass

    @signature
    def impl(a, b, c, d=3, e=5, *, f=5):  # pragma: nocover
        pass

    assert compatible(impl, iface)
    assert not compatible(iface, impl)


def test_allow_reorder_kwonlys():

    @signature
    def foo(a, b, c, *, d, e, f):  # pragma: nocover
        pass

    @signature
    def bar(a, b, c, *, f, d, e):  # pragma: nocover
        pass

    assert compatible(foo, bar)
    assert compatible(bar, foo)


def test_allow_default_changes():

    @signature
    def foo(a, b, c=3, *, d=1, e, f):  # pragma: nocover
        pass

    @signature
    def bar(a, b, c=5, *, f, e, d=12):  # pragma: nocover
        pass

    assert compatible(foo, bar)
    assert compatible(bar, foo)


def test_disallow_kwonly_to_positional():

    @signature
    def foo(a, *, b):  # pragma: nocover
        pass

    @signature
    def bar(a, b):  # pragma: nocover
        pass

    assert not compatible(foo, bar)
    assert not compatible(bar, foo)
