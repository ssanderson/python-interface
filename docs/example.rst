Examples
--------

Suppose we're writing an application that needs to load and save user
preferences.

We expect that we may want to manage preferences differently in different
contexts, so we separate out our preference-management code into its own class,
and our main application looks like this:

.. code-block:: python

   class MyApplication:

       def __init__(self, preferences):
           self.preferences = preferences

       def save_resolution(self, resolution):
           self.preferences.set('resolution', resolution)

       def get_resolution(self):
           return self.preferences.get('resolution')

       def save_volume(self, volume):
           self.preferences.set('volume', volume)

       def get_volume(self):
           return self.preferences.get('volume')

       ...

When we ship our application to users, we store preferences as a json file on
the local hard drive:

.. code-block:: python

   class JSONFileStore:

       def __init__(self, path):
           self.path = path

       def get(self, key):
           with open(self.path) as f:
               return json.load(f)[key]

       def set(self, key, value):
           with open(self.path) as f:
               data = json.load(f)

           data[key] = value

           with open(self.path, 'w') as f:
               json.dump(data, f)

In testing, however, we want to use a simpler key-value store that stores
preferences in memory:

.. code-block:: python

   class InMemoryStore:

       def __init__(self):
           self.data = {}

       def get(self, key):
           return self.data[key]

       def set(self, key, value):
           self.data[key] = value

Later on, we add a cloud-sync feature to our application, so we add a third
implementation that stores user preferences in a database:

.. code-block:: python

   class SQLStore:
       def __init__(self, user, connection):
           self.user = user
           self.connection = connection

       def get(self, key):
           self.connection.execute(
               "SELECT * FROM preferences where key=%s and user=%s",
               [self.key, self.user],
           )

       def set(self, key, value):
           self.connection.execute(
               "INSERT INTO preferences VALUES (%s, %s, %s)",
               [self.user, self.key, value],
   )

As the number of ``KeyValueStore`` implementations grows, it becomes more and
more difficult for us to make changes to our application. If we add a new
method to any of the key-value stores, we can't use it in the application
unless we add the same method to the other implementations, but in a large
codebase we might not even know what other implementations exist!

By declaring ``KeyValueStore`` as an :class:`~interface.Interface` we can get
:mod:`interface` to help us keep our implementations in sync:

.. code-block:: python

   class KeyValueStore(interface.Interface):

       def get(self, key):
           pass

       def set(self, key, value):
           pass

   class JSONFileStore(implements(KeyValueStore)):
       ...

   class InMemoryStore(implements(KeyValueStore)):
       ...

   class SQLStore(implements(KeyValueStore)):
       ...

Now, if we add a method to the interface without adding it to an
implementation, we'll get a helpful error at class definition time.

For example, if we add a ``get_default`` method to the interface but forget to
add it to ``SQLStore``:

.. code-block:: python

   class KeyValueStore(interface.Interface):

       def get(self, key):
           pass

       def set(self, key, value):
           pass

       def get_default(self, key, default):
           pass


   class SQLStore(interface.implements(KeyValueStore)):

       def get(self, key):
           pass

       def set(self, key, value):
           pass

       # We forgot to define get_default!

We get the following error at import time:

::

   $ python example.py
   Traceback (most recent call last):
     File "example.py", line 16, in <module>
       class SQLStore(interface.implements(KeyValueStore)):
     File "/home/ssanderson/projects/interface/interface/interface.py", line 394, in __new__
       raise errors[0]
     File "/home/ssanderson/projects/interface/interface/interface.py", line 376, in __new__
       defaults_from_iface = iface.verify(newtype)
     File "/home/ssanderson/projects/interface/interface/interface.py", line 191, in verify
       raise self._invalid_implementation(type_, missing, mistyped, mismatched)
   interface.interface.InvalidImplementation:
   class SQLStore failed to implement interface KeyValueStore:

   The following methods of KeyValueStore were not implemented:
     - get_default(self, key, default)
