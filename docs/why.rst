Why Interfaces?
---------------

What is an Interface?
~~~~~~~~~~~~~~~~~~~~~

In software generally, an **interface** is a description of the
**capabilities** provided by a unit of code. In object-oriented languages like
Python, interfaces are often defined by lists of **method signatures** which
must be provided by a class.

In :mod:`interface`, an interface is a subclass of :class:`interface.Interface`
that defines a list of methods with empty bodies. For example, the interface
definition for a simple `Key-Value Store`_ might look like this:

.. code-block:: python

   class KeyValueStore(interface.Interface):

       def get(self, key):
           pass

       def set(self, key, value):
           pass

Why Are Interfaces Useful?
~~~~~~~~~~~~~~~~~~~~~~~~~~

Interfaces are useful for specifying the **contract** between two units of
code. By marking that a type **implements** an interface, we give a
programatically-verifiable guarantee that the implementation provides the
methods specified by the interface signature. That guarantee makes it easier to
write code that can work with **any** implementation of an interface, and it
also serves as a form of documentation.

.. _`Key-Value Store` : https://en.wikipedia.org/wiki/Key-value_database
