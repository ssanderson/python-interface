from inspect import signature

from ..typecheck import compatible


def test_compatible_when_equal():

    @signature
    def foo(a, b, c):  # pragma: nocover
        pass

    assert compatible(foo, foo)

    @signature
    def bar():  # pragma: nocover
        pass

    assert compatible(bar, bar)


def test_allow_new_params_with_defaults():

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


def test_disallow_new_or_missing_positionals():

    @signature
    def foo(a, b):  # pragma: nocover
        pass

    @signature
    def bar(a):  # pragma: nocover
        pass

    assert not compatible(foo, bar)
    assert not compatible(bar, foo)


def test_disallow_remove_defaults():

    @signature
    def iface(a, b=3):  # pragma: nocover
        pass

    @signature
    def impl(a, b):  # pragma: nocover
        pass

    assert not compatible(impl, iface)


def test_disallow_reorder_positionals():

    @signature
    def foo(a, b):  # pragma: nocover
        pass

    @signature
    def bar(b, a):  # pragma: nocover
        pass

    assert not compatible(foo, bar)
    assert not compatible(bar, foo)


def test_disallow_kwonly_to_positional():

    @signature
    def foo(a, *, b):  # pragma: nocover
        pass

    @signature
    def bar(a, b):  # pragma: nocover
        pass

    assert not compatible(foo, bar)
    assert not compatible(bar, foo)
