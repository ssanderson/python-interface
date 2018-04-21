:mod:`interface`
================

:mod:`interface` is a library for declaring interfaces and for statically
asserting that classes implement those interfaces. It provides stricter
semantics than Python's built-in :mod:`abc` module, and it aims to produce
`exceptionally useful error messages`_ when interfaces aren't satisfied.

:mod:`interface` supports Python 2.7 and Python 3.4+.

Quick Start
-----------

.. code-block:: python

   from interface import implements, Interface

   class MyInterface(Interface):

       def method1(self, x):
           pass

       def method2(self, x, y):
           pass


   class MyClass(implements(MyInterface)):

       def method1(self, x):
           return x * 2

       def method2(self, x, y):
           return x + y


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   why.rst
   usage.rst
   errors.rst
   abc.rst
   example.rst
   api-reference.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`exceptionally useful error messages` : errors.html
