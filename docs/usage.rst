Using :mod:`interface`
----------------------

Declaring Interfaces
~~~~~~~~~~~~~~~~~~~~

An interface describes a collection of methods and properties that should be
provided by implementors.

We create an interface by subclassing from :class:`interface.Interface` and
defining stubs for methods that should be part of the interface:

.. code-block:: python

   class MyInterface(interface.Interface):

       def method1(self, x, y, z):
           pass

       def method2(self):
           pass

Implementing Interfaces
~~~~~~~~~~~~~~~~~~~~~~~

To declare that a class implements an interface ``I``, that class should
subclass from ``implements(I)``:

.. code-block:: python

   class MyClass(interface.implements(MyInterface)):

       def method1(self, x, y, z):
           return x + y + z

       def method2(self):
           return "foo"

A class can implement more than one interface:

.. code-block:: python

   class MathStudent(Interface):

       def argue(self, topic):
           pass

       def calculate(self, x, y):
           pass


   class PhilosophyStudent(Interface):

       def argue(self, topic):
           pass

       def pontificate(self):
           pass


   class LiberalArtsStudent(implements(MathStudent, PhilosophyStudent)):

       def argue(self, topic):
           print(topic, "is", ["good", "bad"][random.choice([0, 1])])

       def calculate(self, x, y):
           return x + y

       def pontificate(self):
           print("I think what Wittgenstein was **really** saying is...")

Notice that interfaces can have intersecting methods as long as their
signatures match.

Properties
~~~~~~~~~~

Interfaces can declare non-method attributes that should be provided by
implementations using :class:`property`:

.. code-block:: python

   class MyInterface(interface.Interface):

       @property
       def my_property(self):
           pass

Implementations are required to provide a :class:`property` with the same name.

.. code-block:: python

   class MyClass(interface.implements(MyInterface)):

       @property
       def my_property(self):
           return 3

Default Implementations
~~~~~~~~~~~~~~~~~~~~~~~

Sometimes we have a method that should be part of an interface, but which can
be implemented in terms of other interface methods. When this happens, you can
use :class:`interface.default` to provide a default implementation of a method.

.. code-block:: python

   class ReadOnlyMapping(interface.Interface):

       def get(self, key):
           pass

       def keys(self):
           pass

       @interface.default
       def get_all(self):
           out = {}
           for k in self.keys():
               out[k] = self.get(k)
           return out

Implementors are not required to implement methods with defaults:

.. code-block:: python

   class MyReadOnlyMapping(interface.implements(ReadOnlyMapping)):
       def __init__(self, data):
           self._data = data

       def get(self, key):
           return self._data[key]

       def keys(self):
           return self._data.keys()

       # get_all(self) will automatically be copied from the interface default.

Default implementations should always be implemented in terms of other
interface methods.

In Python 3, :class:`default` will show a warning if a default implementation
uses non-interface members of an object:

.. code-block:: python

   class ReadOnlyMapping(interface.Interface):

       def get(self, key):
           pass

       def keys(self):
           pass

       @interface.default
       def get_all(self):
           # This is supposed to be a default implementation for **any**
           # ReadOnlyMapping, but this implementation assumes that 'self' has
           # an _data attribute that isn't part of the interface!
           return self._data.keys()

Running the above example displays a warning about the default implementation
of ``get_all``:

::

   $ python example.py
   example.py:4: UnsafeDefault: Default for ReadOnlyMapping.get_all uses non-interface attributes.

   The following attributes are used but are not part of the interface:
     - _data

   Consider changing ReadOnlyMapping.get_all or making these attributes part of ReadOnlyMapping.
      class ReadOnlyMapping(interface.Interface):

Default Properties
******************

:class:`default` and :class:`property` can be used together to create default properties:

.. code-block:: python

   class ReadOnlyMappingWithSpecialKey(interface.Interface):

       def get(self, key):
           pass

       @interface.default
       @property
       def special_key(self):
           return self.get('special_key')

.. note::

   The order of decorators in the example above is important: ``@default`` must
   go above ``@property``.

Interface Subclassing
~~~~~~~~~~~~~~~~~~~~~

Interfaces can inherit requirements from other interfaces via subclassing. For
example, if we want to create interfaces for read-write and read-only mappings,
we could do so as follows:

.. code-block:: python

   class ReadOnlyMapping(interface.Interface):
       def get(self, key):
           pass

       def keys(self):
           pass


   class ReadWriteMapping(ReadOnlyMapping):

       def set(self, key, value):
           pass

       def delete(self, key):
           pass


An interface that subclasses from another interface inherits all the function
signature requirements from its parent interface. In the example above, a class
implementing ``ReadWriteMapping`` would have to implement ``get``, ``keys``,
``set``, and ``delete``.

.. warning::

   Subclassing from an interface is not the same as implementing an
   interface. Subclassing from an interface **creates a new interface** that
   adds additional methods to the parent interface. Implementing an interface
   creates a new class whose method signatures must be compatible with the
   interface being implemented.
