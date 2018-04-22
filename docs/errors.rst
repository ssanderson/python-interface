Error Detection
---------------

:mod:`interface` aims to provide clear, detailed, and complete error messages
when an interface definition isn't satisfied.

An implementation can fail to implement an interface in a variety of ways:

Missing Methods
~~~~~~~~~~~~~~~

Implementations must define all the methods declared in an interface.

.. code-block:: python

   from interface import implements, Interface

   class MathStudent(Interface):

       def argue(self, topic):
           pass

       def prove(self, theorem):
           pass

       def calculate(self, x, y, z):
           pass


   class Freshman(implements(MathStudent)):

       def argue(self, topic):
           print(topic, "is terrible!")

The above example produces the following error message::

  Traceback (most recent call last):
    ...
  interface.interface.InvalidImplementation:
  class Freshman failed to implement interface MathStudent:

  The following methods of MathStudent were not implemented:
    - calculate(self, x, y, z)
    - prove(self, theorem)

Methods with Incompatible Signatures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implementations must define interface methods with compatible signatures:

.. code-block:: python

   from interface import implements, Interface

   class MathStudent(Interface):

       def argue(self, topic):
           pass

       def prove(self, theorem):
           pass

       def calculate(self, x, y, z):
           pass


   class SloppyMathStudent(implements(MathStudent)):

       def argue(self, topic):
           print(topic, "is terrible!")

       def prove(self, lemma):
           print("That's almost a theorem, right?")

       def calculate(self, x, y):
           return x + y

::

   Traceback (most recent call last):
     ...
   interface.interface.InvalidImplementation:
   class SloppyMathStudent failed to implement interface MathStudent:

   The following methods of MathStudent were implemented with invalid signatures:
     - calculate(self, x, y) != calculate(self, x, y, z)
     - prove(self, lemma) != prove(self, theorem)

Method/Property Mismatches
~~~~~~~~~~~~~~~~~~~~~~~~~~

If an interface defines an attribute as a :class:`property`, the corresponding
implementation attribute must also be a :class:`property`:

.. code-block:: python

   class Philosopher(Interface):
       @property
       def favorite_philosopher(self):
           pass

   class AnalyticPhilosopher(implements(Philosopher)):

       def favorite_philosopher(self):  # oops, should have been a property!
           return "Ludwig Wittgenstein"

::
   Traceback (most recent call last):
     ...
   interface.interface.InvalidImplementation:
   class AnalyticPhilosopher failed to implement interface Philosopher:

   The following methods of Philosopher were implemented with incorrect types:
     - favorite_philosopher: 'function' is not a subtype of expected type 'property'
