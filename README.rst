``interface``
=============

|build status|

``interface`` provides facilities for declaring interfaces and for statically
asserting that classes implement those interfaces. It supports Python 2.7 and
Python 3.4+.

``interface`` improves on Python's ``abc`` module in two ways:

1. Interface requirements are checked at class creation time, rather than at
   instance creation time.  This means that ``interface`` can tell you if a
   class fails to meet the requirements of an interface even if you never
   create any instances of that class.

2. ``interface`` requires that method signatures of interface implementations
   are compatible with the signatures declared in the interface.  For example,
   the following code using ``abc`` does not produce an error:

   .. code-block:: python

      >>> from abc import ABCMeta, abstractmethod
      >>> class Base(metaclass=ABCMeta):
      ...     @abstractmethod
      ...     def method(self, a, b):
      ...         pass
      ...
      >>> class Implementation(MyABC):
      ...     def method(self):
      ...         return "This shouldn't work."
      ...
      >>> impl = Implementation()
      >>>

   The equivalent code using ``interface`` produces an error indicating that
   the signature of our implementation method is incompatible with the
   signature of our interface declaration:

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

Defining an Interface
~~~~~~~~~~~~~~~~~~~~~

To define an interface, simply subclass from ``interface.Interface`` and define
method stubs in your class body.

.. code-block:: python

   from interface import Interface

   class MyInterface(Interface):

       def method1(self):
           pass

       def method2(self, arg1, arg2):
           pass

Implementing an Interface
~~~~~~~~~~~~~~~~~~~~~~~~~

To declare that a particular class implements an interface ``I``, pass
``implements(I)`` as a base class for your class.

.. code-block:: python

   from interface import implements

   class MyClass(implements(MyInterface)):

       def method1(self):
           return "method1"

       def method2(self, arg1, arg2):
           return "method2"

Installation
~~~~~~~~~~~~

.. code-block:: shell

   $ pip install python-interface

.. |build status| image:: https://travis-ci.org/ssanderson/interface.svg?branch=master
   :target: https://travis-ci.org/ssanderson/interface
