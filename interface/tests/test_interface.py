import pytest
from textwrap import dedent

from ..compat import PY3, wraps
from ..interface import implements, InvalidImplementation, Interface, default
from ..default import UnsafeDefault


py3_only = pytest.mark.skipif(not PY3, reason="Python 3 Only")


def test_valid_implementation():

    class I(Interface):  # pragma: nocover

        def m0(self):
            pass

        def m1(self, x):
            pass

        def m2(self, y):
            pass

    class C(implements(I)):  # pragma: nocover
        def m0(self):
            pass

        def m1(self, x):
            pass

        def m2(self, y):
            pass

    for i in range(10):
        class C(C):
            pass


def test_implement_multiple_interfaces_correctly():

    class I1(Interface):  # pragma: nocover
        def i1_method(self, arg1):
            pass

        def shared(self, a, b, c):
            pass

    class I2(Interface):  # pragma: nocover
        def i2_method(self, arg2):
            pass

        def shared(self, a, b, c):
            pass

    class C(implements(I1), implements(I2)):  # pragma: nocover
        def i1_method(self, arg1):
            pass

        def i2_method(self, arg2):
            pass

        def shared(self, a, b, c):
            pass

    assert set(C.interfaces()) == set([I1, I2])


def generative_fixture(g):
    """
    Decorator for turning a generator into a "parameterized" fixture that emits
    the generated values.
    """
    fixture_values = list(g())

    @pytest.fixture(params=fixture_values)
    def _fixture(request):
        return request.param

    return _fixture


@generative_fixture
def combine_interfaces():

    def combine_with_multiple_types(*interfaces):
        return tuple(map(implements, interfaces))

    def combine_with_single_type(*interfaces):
        return (implements(*interfaces),)

    yield combine_with_multiple_types
    yield combine_with_single_type


def test_require_implement_all_interfaces(combine_interfaces):

    class I1(Interface):  # pragma: nocover
        def i1_method(self, arg1):
            pass

        def shared(self, a, b, c):
            pass

    class I2(Interface):  # pragma: nocover
        def i2_method(self, arg2):
            pass

        def shared(self, a, b, c):
            pass

    bases = combine_interfaces(I1, I2)

    with pytest.raises(InvalidImplementation):
        type('C', bases, {
            'i1_method': lambda self, arg1: None,
            'i2_method': lambda self, arg2: None,
        })

    with pytest.raises(InvalidImplementation):
        type('C', bases, {
            'i1_method': lambda self, arg1: None,
            'i2_method': lambda self, a, b, c: None,
        })

    with pytest.raises(InvalidImplementation):

        type('C', bases, {
            'i2_method': lambda self, arg2: None,
            'shared': lambda self, a, b, c: None,
        })


def test_missing_methods():

    class I(Interface):  # pragma: nocover

        def m0(self):
            pass

        def m1(self):
            pass

        def m2(self, x):
            pass

    try:
        class C(implements(I)):
            def m0(self):  # pragma: nocover
                pass
    except InvalidImplementation as e:
        actual = str(e)
        expected = dedent(
            """
            class C failed to implement interface I:

            The following methods of I were not implemented:
              - m1(self)
              - m2(self, x)"""
        )
        assert actual == expected
    else:
        pytest.fail("Should have raised InvalidImplementation.")  # pragma: nocover


def test_incompatible_methods():

    class I(Interface):  # pragma: nocover

        def m0(self):
            pass

        def m1(self, x):
            pass

        def m2(self, x):
            pass

    try:
        class C(implements(I)):  # pragma: nocover
            def m0(self):
                pass

            def m1(self, y):
                pass

            def m2(self, x, y):
                pass

    except InvalidImplementation as e:
        actual = str(e)
        expected = dedent(
            """
            class C failed to implement interface I:

            The following methods of I were implemented with invalid signatures:
              - m1(self, y) != m1(self, x)
              - m2(self, x, y) != m2(self, x)"""
        )
        assert actual == expected
    else:
        pytest.fail("Should have raised InvalidImplementation.")  # pragma: nocover


def test_fail_multiple_interfaces():

    class I(Interface):  # pragma: nocover
        def m0(self, a):
            pass

    class J(Interface):  # pragma: nocover
        def m1(self, a):
            pass

    try:
        class D(implements(I, J)):  # pragma: nocover
            def m1(self, z):  # incorrect signature
                pass
    except InvalidImplementation as e:
        actual = str(e)
        expected = dedent(
            """
            class D failed to implement interface I:

            The following methods of I were not implemented:
              - m0(self, a)

            class D failed to implement interface J:

            The following methods of J were implemented with invalid signatures:
              - m1(self, z) != m1(self, a)"""
        )
        assert actual == expected


def test_implements_memoization():

    class I(Interface):
        pass

    class OtherI(Interface):
        pass

    assert implements(I) is implements(I)
    assert implements(I) is not implements(OtherI)


def test_reject_invalid_interface():

    with pytest.raises(TypeError):
        implements()

    class NotAnInterface:
        pass

    with pytest.raises(TypeError):
        implements(NotAnInterface)


def test_generated_attributes():

    class IFace(Interface):  # pragma: nocover
        def method(self, a, b):
            pass

        def method2(self, a, b, c):
            pass

    class OtherIFace(Interface):  # pragma: nocover

        def method3(self, a, b, c):
            pass

    impl = implements(IFace, OtherIFace)
    assert impl.__name__ == "ImplementsIFace_OtherIFace"

    expected_doc = dedent(
        """\
        Implementation of IFace, OtherIFace.

        Methods
        -------
        IFace.method(self, a, b)
        IFace.method2(self, a, b, c)
        OtherIFace.method3(self, a, b, c)"""
    )
    assert impl.__doc__ == expected_doc


def test_cant_instantiate_interface():

    class I(Interface):
        pass

    with pytest.raises(TypeError):
        I()


def test_reject_non_callable_interface_field():

    with pytest.raises(TypeError) as e:
        class IFace(Interface):
            x = "not allowed"


def test_static_method():

    class I(Interface):
        @staticmethod
        def foo(a, b):  # pragma: nocover
            pass

    class my_staticmethod(staticmethod):
        pass

    class Impl(implements(I)):
        @my_staticmethod   # allow staticmethod subclasses
        def foo(a, b):  # pragma: nocover
            pass

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(I)):
            @staticmethod
            def foo(self, a, b):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Impl failed to implement interface I:

        The following methods of I were implemented with invalid signatures:
          - foo(self, a, b) != foo(a, b)"""
    )
    assert expected == str(e.value)

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(I)):
            def foo(a, b):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Impl failed to implement interface I:

        The following methods of I were implemented with incorrect types:
          - foo: 'function' is not a subtype of expected type 'staticmethod'"""
    )
    assert expected == str(e.value)


def test_class_method():

    class I(Interface):
        @classmethod
        def foo(cls, a, b):  # pragma: nocover
            pass

    class my_classmethod(classmethod):
        pass

    class Impl(implements(I)):
        @my_classmethod
        def foo(cls, a, b):  # pragma: nocover
            pass

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(I)):
            @classmethod
            def foo(a, b):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Impl failed to implement interface I:

        The following methods of I were implemented with invalid signatures:
          - foo(a, b) != foo(cls, a, b)"""
    )
    assert expected == str(e.value)

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(I)):
            def foo(cls, a, b):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Impl failed to implement interface I:

        The following methods of I were implemented with incorrect types:
          - foo: 'function' is not a subtype of expected type 'classmethod'"""
    )
    assert expected == str(e.value)


def test_property():

    class I(Interface):
        @property
        def foo(self):  # pragma: nocover
            pass

    class my_property(property):
        pass

    class Impl(implements(I)):
        @my_property
        def foo(self):  # pragma: nocover
            pass

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(I)):
            def foo(self):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Impl failed to implement interface I:

        The following methods of I were implemented with incorrect types:
          - foo: 'function' is not a subtype of expected type 'property'"""
    )
    assert expected == str(e.value)

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(I)):
            @property
            def foo(self, a, b):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Impl failed to implement interface I:

        The following methods of I were implemented with invalid signatures:
          - foo(self, a, b) != foo(self)"""
    )
    assert expected == str(e.value)

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(I)):
            def foo(self, a, b):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Impl failed to implement interface I:

        The following methods of I were implemented with incorrect types:
          - foo: 'function' is not a subtype of expected type 'property'

        The following methods of I were implemented with invalid signatures:
          - foo(self, a, b) != foo(self)"""
    )
    assert expected == str(e.value)


def test_subclass_implements_additional_interface():

    class I1(Interface):
        def method1(self):  # pragma: nocover
            pass

    class I2(Interface):
        def method2(self):  # pragma: nocover
            pass

    class Impl1(implements(I1)):
        def method1(self):  # pragma: nocover
            pass

    with pytest.raises(InvalidImplementation) as e:
        class IncorrectImpl2(Impl1, implements(I2)):
            pass

    expected = dedent(
        """
        class IncorrectImpl2 failed to implement interface I2:

        The following methods of I2 were not implemented:
          - method2(self)"""
    )

    assert expected == str(e.value)

    with pytest.raises(InvalidImplementation) as e:
        class Implement2ButBreak1(Impl1, implements(I2)):

            def method1(self, x):  # pragma: nocover
                pass

            def method2(self):  # pragma: nocover
                pass

    expected = dedent(
        """
        class Implement2ButBreak1 failed to implement interface I1:

        The following methods of I1 were implemented with invalid signatures:
          - method1(self, x) != method1(self)"""
    )

    assert expected == str(e.value)


def test_default():

    class IFace(Interface):  # pragma: nocover

        def method1(self):
            pass

        def method2(self):
            pass

        @default
        def has_default(self):
            return self.method1() + self.method2()

    class C(implements(IFace)):  # pragma: nocover

        def method1(self):
            return 1

        def method2(self):
            return 2

    assert C().has_default() == 3


def test_override_default():

    class IFace(Interface):  # pragma: nocover

        @default
        def default(self):
            return 'ayy'

    class C(implements(IFace)):  # pragma: nocover

        def default(self):
            return 'lmao'

    assert C().default() == 'lmao'


def test_conflicting_defaults():

    class IFace1(Interface):  # pragma: nocover

        def foo(self, a, b, c):
            pass

        @default
        def has_default(self, x):
            pass

    class IFace2(Interface):  # pragma: nocover

        def bar(self, x, y, z):
            pass

        @default
        def has_default(self, x):
            pass

    with pytest.raises(InvalidImplementation) as e:
        class Impl(implements(IFace1, IFace2)):  # pragma: nocover
            def foo(self, a, b, c):
                return a + b + c

            def bar(self, x, y, z):
                return x + y + z

    actual = str(e.value)
    expected = dedent(
        """
        class Impl received conflicting default implementations:

        The following interfaces provided default implementations for 'has_default':
          - IFace1
          - IFace2"""
    )
    assert actual == expected


def test_default_repr():

    @default
    def foo(a, b):  # pragma: nocover
        pass

    assert repr(foo) == "default({})".format(foo.implementation)


@py3_only
def test_default_warns_if_method_uses_non_interface_methods():  # pragma: nocover-py2

    with pytest.warns(UnsafeDefault) as warns:

        class HasDefault(Interface):

            def interface_method(self, x):
                pass

            @default
            def foo(self, a, b):
                # Shouldn't cause warnings.
                self.default_method()
                self.default_classmethod()
                self.default_staticmethod()
                self.interface_method(a)

            @default
            def probably_broken_method_with_no_args():
                # This is a weird thing to do, but it shouldn't cause us to
                # crash because of missing a first parameter.
                pass

            @default
            @classmethod
            def probably_broken_classmethod_with_no_args():
                # This is a weird thing to do, but it shouldn't cause us to
                # crash because of missing a first parameter.
                pass

            @default
            @property
            def probably_broken_property_with_no_args():
                # This is a weird thing to do, but it shouldn't cause us to
                # crash because of missing a first parameter.
                pass

            @default
            @staticmethod
            def default_staticmethod():
                # Shouldn't cause warnings.
                global some_nonexistent_method
                return some_nonexistent_method()

            @default
            def default_method(self, x):
                foo = self.foo(1, 2)  # Should be fine.
                wut = self.not_in_interface(2, 3)  # Should cause a warning.
                self.setting_non_interface = 2  # Should cause a warning.
                return foo + wut

            @default
            @classmethod
            def default_classmethod(cls, x):
                return cls.class_bar(2, 3)  # Should cause a warning.

    messages = warns.list
    assert len(messages) == 2

    first = str(messages[0].message)
    expected_first = """\
Default for HasDefault.default_classmethod uses non-interface attributes.

The following attributes are used but are not part of the interface:
  - class_bar

Consider changing HasDefault.default_classmethod or making these attributes part of HasDefault."""  # noqa
    assert first == expected_first

    second = str(messages[1].message)
    expected_second = """\
Default for HasDefault.default_method uses non-interface attributes.

The following attributes are used but are not part of the interface:
  - not_in_interface
  - setting_non_interface

Consider changing HasDefault.default_method or making these attributes part of HasDefault."""  # noqa
    assert second == expected_second


def test_wrapped_implementation():
    class I(Interface):  # pragma: nocover
        def f(self, a, b, c):
            pass

    def wrapping_decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):  # pragma: nocover
            pass

        return inner

    class C(implements(I)):  # pragma: nocover
        @wrapping_decorator
        def f(self, a, b, c):
            pass


def test_wrapped_implementation_incompatible():
    class I(Interface):  # pragma: nocover
        def f(self, a, b, c):
            pass

    def wrapping_decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):  # pragma: nocover
            pass

        return inner

    with pytest.raises(InvalidImplementation) as e:
        class C(implements(I)):  # pragma: nocover
            @wrapping_decorator
            def f(self, a, b):  # missing ``c``
                pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class C failed to implement interface I:

        The following methods of I were implemented with invalid signatures:
          - f(self, a, b) != f(self, a, b, c)"""
    )

    assert actual_message == expected_message


@pytest.mark.parametrize('name', ['MyInterface', None])
def test_interface_from_class(name):

    class MyClass(object):  # pragma: nocover
        def method1(self, x):
            raise AssertionError("method1 called")

        def method2(self, y):
            raise AssertionError("method2 called")

    iface = Interface.from_class(MyClass, name=name)

    if name is None:
        expected_name = 'MyClassInterface'
    else:
        expected_name = name

    assert iface.__name__ == expected_name

    with pytest.raises(InvalidImplementation) as e:
        class C(implements(iface)):  # pragma: nocover
            pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class C failed to implement interface {iface}:

        The following methods of {iface} were not implemented:
          - method1(self, x)
          - method2(self, y)"""
    ).format(iface=expected_name)

    assert actual_message == expected_message


def test_interface_from_class_method_subset():

    class C(object):  # pragma: nocover

        def method1(self, x):
            pass

        def method2(self, y):
            pass

    iface = Interface.from_class(C, subset=['method1'])

    class Impl(implements(iface)):  # pragma: nocover
        def method1(self, x):
            pass

    with pytest.raises(InvalidImplementation) as e:

        class BadImpl(implements(iface)):  # pragma: nocover
            def method2(self, y):
                pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class BadImpl failed to implement interface CInterface:

        The following methods of CInterface were not implemented:
          - method1(self, x)"""
    )

    assert actual_message == expected_message


def test_interface_from_class_inherited_methods():

    class Base(object):  # pragma: nocover
        def base_method(self, x):
            pass

    class Derived(Base):  # pragma: nocover
        def derived_method(self, y):
            pass

    iface = Interface.from_class(Derived)

    # Should be fine
    class Impl(implements(iface)):  # pragma: nocover
        def base_method(self, x):
            pass

        def derived_method(self, y):
            pass

    with pytest.raises(InvalidImplementation) as e:

        class BadImpl(implements(iface)):  # pragma: nocover
            def derived_method(self, y):
                pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class BadImpl failed to implement interface DerivedInterface:

        The following methods of DerivedInterface were not implemented:
          - base_method(self, x)"""
    )
    assert actual_message == expected_message

    with pytest.raises(InvalidImplementation) as e:

        class BadImpl(implements(iface)):  # pragma: nocover
            def base_method(self, x):
                pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class BadImpl failed to implement interface DerivedInterface:

        The following methods of DerivedInterface were not implemented:
          - derived_method(self, y)"""
    )

    assert actual_message == expected_message


def test_interface_from_class_magic_methods():

    class HasMagicMethods(object):  # pragma: nocover
        def __getitem__(self, key):
            return key

    iface = Interface.from_class(HasMagicMethods)

    # Should be fine
    class Impl(implements(iface)):  # pragma: nocover
        def __getitem__(self, key):
            return key

    with pytest.raises(InvalidImplementation) as e:

        class BadImpl(implements(iface)):  # pragma: nocover
            pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class BadImpl failed to implement interface HasMagicMethodsInterface:

        The following methods of HasMagicMethodsInterface were not implemented:
          - __getitem__(self, key)"""
    )
    assert actual_message == expected_message
