:mod:`interface` vs. :mod:`abc`
-------------------------------

The Python standard library :mod:`abc` (**A**\bstract **B**\ase **C**\lass)
module is often used to define and verify interfaces.

:mod:`interface` differs from Python's :mod:`abc` module in two important ways:

1. Interface requirements are checked at class creation time, rather than at
   instance creation time. This means that :mod:`interface` can tell you if a
   class fails to implement an interface even if you never create any instances
   of that class.

2. :mod:`interface` requires that method signatures of implementations are
   compatible with signatures declared in interfaces. For example, the
   following code using :mod:`abc` does not produce an error:

   .. code-block:: python

      >>> from abc import ABCMeta, abstractmethod
      >>> class Base(metaclass=ABCMeta):
      ...
      ...     @abstractmethod
      ...     def method(self, a, b):
      ...         pass
      ...
      >>> class Implementation(MyABC):
      ...
      ...     def method(self):  # Missing a and b parameters.
      ...         return "This shouldn't work."
      ...
      >>> impl = Implementation()
      >>>

   The equivalent code using :mod:`interface` produces an error telling us that
   the implementation method doesn't match the interface:

   .. code-block:: python

      >>> from interface import implements, Interface
      >>> class I(Interface):
      ...     def method(self, a, b):
      ...         pass
      ...
      >>> class C(implements(I)):
      ...     def method(self):
      ...         return "This shouldn't work"
      ...
      TypeError:
      class C failed to implement interface I:

      The following methods were implemented but had invalid signatures:
        - method(self) != method(self, a, b)
