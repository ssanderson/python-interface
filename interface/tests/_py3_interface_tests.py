from textwrap import dedent

import pytest

from ..interface import implements, Interface, InvalidImplementation


def test_async_interface_sync_impl():

    class AsyncInterface(Interface):
        async def foo(self, a, b):  # pragma: nocover
            pass

    # This should pass.
    class AsyncImpl(implements(AsyncInterface)):
        async def foo(self, a, b):  # pragma: nocover
            pass

    # This should barf because foo isn't async.
    with pytest.raises(InvalidImplementation) as e:
        class SyncImpl(implements(AsyncInterface)):
            def foo(self, a, b):  # pragma: nocover
                pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class SyncImpl failed to implement interface AsyncInterface:

        The following methods of AsyncInterface were implemented with invalid signatures:
          - foo(self, a, b) != async foo(self, a, b)"""
    )
    assert actual_message == expected_message


def test_sync_interface_async_impl():

    class SyncInterface(Interface):
        def foo(self, a, b):  # pragma: nocover
            pass

    with pytest.raises(InvalidImplementation) as e:
        class AsyncImpl(implements(SyncInterface)):
            async def foo(self, a, b):  # pragma: nocover
                pass

    actual_message = str(e.value)
    expected_message = dedent(
        """
        class AsyncImpl failed to implement interface SyncInterface:

        The following methods of SyncInterface were implemented with invalid signatures:
          - async foo(self, a, b) != foo(self, a, b)"""
    )
    assert actual_message == expected_message
