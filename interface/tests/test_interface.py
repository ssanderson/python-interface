import pytest
from textwrap import dedent

from ..interface import implements, Interface


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
    except TypeError as e:
        actual = str(e)
        expected = dedent(
            """\
            class C failed to implement interface I:

            The following methods were not implemented:
              - m1(self)
              - m2(self, x)"""
        )
        assert actual == expected
    else:
        pytest.fail("Should have raised TypeError.")  # pragma: nocover


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

    except TypeError as e:
        actual = str(e)
        expected = dedent(
            """\
            class C failed to implement interface I:

            The following methods were implemented but had invalid signatures:
              - m1(self, y) != m1(self, x)
              - m2(self, x, y) != m2(self, x)"""
        )
        assert actual == expected
    else:
        pytest.fail("Should have raised TypeError.")  # pragma: nocover


def test_implements_memoization():

    class I(Interface):
        pass

    class OtherI(Interface):
        pass

    assert implements(I) is implements(I)
    assert implements(I) is not implements(OtherI)


def test_reject_invalid_interface():

    class NotAnInterface:
        pass

    with pytest.raises(TypeError):
        implements(NotAnInterface)
