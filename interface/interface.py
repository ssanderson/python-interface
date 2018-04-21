from collections import defaultdict
from operator import attrgetter, itemgetter
from textwrap import dedent
from weakref import WeakKeyDictionary

from .compat import raise_from, with_metaclass
from .default import default, warn_if_defaults_use_non_interface_members
from .formatting import bulleted_list
from .functional import complement, keyfilter, valfilter
from .typecheck import compatible
from .typed_signature import TypedSignature
from .utils import is_a, unique

first = itemgetter(0)
getname = attrgetter('__name__')


class InvalidImplementation(TypeError):
    """
    Raised when a class intending to implement an interface fails to do so.
    """


CLASS_ATTRIBUTE_WHITELIST = frozenset([
    '__doc__',
    '__module__',
    '__name__',
    '__qualname__',
    '__weakref__',
])

is_interface_field_name = complement(CLASS_ATTRIBUTE_WHITELIST.__contains__)

TRIVIAL_CLASS_ATTRIBUTES = frozenset(dir(type('_', (object,), {})))


def static_get_type_attr(t, name):
    """
    Get a type attribute statically, circumventing the descriptor protocol.
    """
    for type_ in t.mro():
        try:
            return vars(type_)[name]
        except KeyError:
            pass
    raise AttributeError(name)


def _conflicting_defaults(typename, conflicts):
    """Format an error message for conflicting default implementations.

    Parameters
    ----------
    typename : str
        Name of the type for which we're producing an error.
    conflicts : dict[str -> list[Interface]]
        Map from strings to interfaces providing a default with that name.

    Returns
    -------
    message : str
        User-facing error message.
    """
    message = "\nclass {C} received conflicting default implementations:".format(
        C=typename,
    )
    for attrname, interfaces in conflicts.items():
        message += dedent(
            """

            The following interfaces provided default implementations for {attr!r}:
            {interfaces}"""
        ).format(
            attr=attrname,
            interfaces=bulleted_list(sorted(map(getname, interfaces))),
        )
    return InvalidImplementation(message)


class InterfaceMeta(type):
    """
    Metaclass for interfaces.

    Supplies a ``_signatures`` attribute.
    """
    def __new__(mcls, name, bases, clsdict):
        signatures = {}
        defaults = {}
        for k, v in keyfilter(is_interface_field_name, clsdict).items():
            try:
                signatures[k] = TypedSignature(v)
            except TypeError as e:
                errmsg = (
                    "Couldn't parse signature for field "
                    "{iface_name}.{fieldname} of type {attrtype}.".format(
                        iface_name=name,
                        fieldname=k,
                        attrtype=getname(type(v)),
                    )
                )
                raise_from(TypeError(errmsg), e)

            if isinstance(v, default):
                defaults[k] = v

        warn_if_defaults_use_non_interface_members(
            name,
            defaults,
            set(signatures.keys())
        )

        clsdict['_signatures'] = signatures
        clsdict['_defaults'] = defaults
        return super(InterfaceMeta, mcls).__new__(mcls, name, bases, clsdict)

    def _diff_signatures(self, type_):
        """
        Diff our method signatures against the methods provided by type_.

        Parameters
        ----------
        type_ : type
           The type to check.

        Returns
        -------
        missing, mistyped, mismatched : list[str], dict[str -> type], dict[str -> signature]  # noqa
            ``missing`` is a list of missing interface names.
            ``mistyped`` is a list mapping names to incorrect types.
            ``mismatched`` is a dict mapping names to incorrect signatures.
        """
        missing = []
        mistyped = {}
        mismatched = {}
        for name, iface_sig in self._signatures.items():
            try:
                # Don't invoke the descriptor protocol here so that we get
                # staticmethod/classmethod/property objects instead of the
                # functions they wrap.
                f = static_get_type_attr(type_, name)
            except AttributeError:
                missing.append(name)
                continue

            impl_sig = TypedSignature(f)

            if not issubclass(impl_sig.type, iface_sig.type):
                mistyped[name] = impl_sig.type

            if not compatible(impl_sig.signature, iface_sig.signature):
                mismatched[name] = impl_sig

        return missing, mistyped, mismatched

    def verify(self, type_):
        """
        Check whether a type implements ``self``.

        Parameters
        ----------
        type_ : type
            The type to check.

        Raises
        ------
        TypeError
            If ``type_`` doesn't conform to our interface.

        Returns
        -------
        None
        """
        raw_missing, mistyped, mismatched = self._diff_signatures(type_)

        # See if we have defaults for missing methods.
        missing = []
        defaults_to_use = {}
        for name in raw_missing:
            try:
                defaults_to_use[name] = self._defaults[name].implementation
            except KeyError:
                missing.append(name)

        if not any((missing, mistyped, mismatched)):
            return defaults_to_use

        raise self._invalid_implementation(type_, missing, mistyped, mismatched)

    def _invalid_implementation(self, t, missing, mistyped, mismatched):
        """
        Make a TypeError explaining why ``t`` doesn't implement our interface.
        """
        assert missing or mistyped or mismatched, "Implementation wasn't invalid."

        message = "\nclass {C} failed to implement interface {I}:".format(
            C=getname(t),
            I=getname(self),
        )
        if missing:
            message += dedent(
                """

                The following methods of {I} were not implemented:
                {missing_methods}"""
            ).format(
                I=getname(self),
                missing_methods=self._format_missing_methods(missing)
            )

        if mistyped:
            message += dedent(
                """

                The following methods of {I} were implemented with incorrect types:
                {mismatched_types}"""
            ).format(
                I=getname(self),
                mismatched_types=self._format_mismatched_types(mistyped),
            )

        if mismatched:
            message += dedent(
                """

                The following methods of {I} were implemented with invalid signatures:
                {mismatched_methods}"""
            ).format(
                I=getname(self),
                mismatched_methods=self._format_mismatched_methods(mismatched),
            )
        return InvalidImplementation(message)

    def _format_missing_methods(self, missing):
        return "\n".join(sorted([
            "  - {name}{sig}".format(name=name, sig=self._signatures[name])
            for name in missing
        ]))

    def _format_mismatched_types(self, mistyped):
        return "\n".join(sorted([
            "  - {name}: {actual!r} is not a subtype "
            "of expected type {expected!r}".format(
                name=name,
                actual=getname(bad_type),
                expected=getname(self._signatures[name].type),
            )
            for name, bad_type in mistyped.items()
        ]))

    def _format_mismatched_methods(self, mismatched):
        return "\n".join(sorted([
            "  - {name}{actual} != {name}{expected}".format(
                name=name,
                actual=bad_sig,
                expected=self._signatures[name],
            )
            for name, bad_sig in mismatched.items()
        ]))


class Interface(with_metaclass(InterfaceMeta)):
    """
    Base class for interface definitions.

    An interface defines a set of methods and/or attributes that should be
    provided by one or more classes, which are called "implementations" of the
    interface.

    Classes can declare that they implement an interface ``I`` by subclassing
    ``implements(I)``. During class construction, the base class generated by
    ``implements(I)`` will verify that the new class correctly implements all
    the methods required  by ``I``.

    Interfaces cannot be instantiated.

    Examples
    --------

    **Defining an Interface:**

    .. code-block:: python

        class KeyValueStore(Interface):

            def get(self, key):
                pass

            def set(self, key, value):
                pass

            def delete(self, key):
                pass

    **Implementing an Interface:**

    .. code-block:: python

        class InMemoryKeyValueStore(implements(KeyValueStore)):

            def __init__(self):
                self.data = {}

            def get(self, key):
                return self.data[key]

            def set(self, key, value):
                self.data[key] = value

            def delete(self, key):
                del self.data[key]
    See Also
    --------
    :func:`implements`
    """
    def __new__(cls, *args, **kwargs):
        raise TypeError("Can't instantiate interface %s" % getname(cls))

    @classmethod
    def from_class(cls, existing_class, subset=None, name=None):
        """Create an interface from an existing class.

        Parameters
        ----------
        existing_class : type
            The type from which to extract an interface.
        subset : list[str], optional
            List of methods that should be included in the interface.
            Default is to use all attributes not defined in an empty class.
        name : str, optional
            Name of the generated interface.
            Default is ``existing_class.__name__ + 'Interface'``.

        Returns
        -------
        interface : type
            A new interface class with stubs generated from ``existing_class``.
        """
        if name is None:
            name = existing_class.__name__ + 'Interface'

        if subset is None:
            subset = set(dir(existing_class)) - TRIVIAL_CLASS_ATTRIBUTES

        return InterfaceMeta(
            name,
            (Interface,),
            {name: static_get_type_attr(existing_class, name) for name in subset},
        )


empty_set = frozenset([])


class ImplementsMeta(type):
    """
    Metaclass for implementations of particular interfaces.
    """
    def __new__(mcls, name, bases, clsdict, interfaces=empty_set):
        assert isinstance(interfaces, frozenset)

        newtype = super(ImplementsMeta, mcls).__new__(mcls, name, bases, clsdict)

        if interfaces:
            # Don't do checks on the types returned by ``implements``.
            return newtype

        errors = []
        default_impls = {}
        default_providers = defaultdict(list)
        for iface in sorted(newtype.interfaces(), key=getname):
            try:
                defaults_from_iface = iface.verify(newtype)
                for name, impl in defaults_from_iface.items():
                    default_impls[name] = impl
                    default_providers[name].append(iface)
            except InvalidImplementation as e:
                errors.append(e)

        # The list of providers for `name`, if there's more than one.
        duplicate_defaults = valfilter(lambda ifaces: len(ifaces) > 1, default_providers)
        if duplicate_defaults:
            errors.append(_conflicting_defaults(newtype.__name__, duplicate_defaults))
        else:
            for name, impl in default_impls.items():
                setattr(newtype, name, impl)

        if not errors:
            return newtype
        elif len(errors) == 1:
            raise errors[0]
        else:
            raise InvalidImplementation("\n".join(map(str, errors)))

    def __init__(mcls, name, bases, clsdict, interfaces=empty_set):
        mcls._interfaces = interfaces
        super(ImplementsMeta, mcls).__init__(name, bases, clsdict)

    def interfaces(self):
        for elem in unique(self._interfaces_with_duplicates()):
            yield elem

    def _interfaces_with_duplicates(self):
        for elem in self._interfaces:
            yield elem

        for t in filter(is_a(ImplementsMeta), self.mro()):
            for elem in t._interfaces:
                yield elem


def format_iface_method_docs(I):
    iface_name = getname(I)
    return "\n".join([
        "{iface_name}.{method_name}{sig}".format(
            iface_name=iface_name,
            method_name=method_name,
            sig=sig,
        )
        for method_name, sig in sorted(list(I._signatures.items()), key=first)
    ])


def _make_implements():
    _memo = WeakKeyDictionary()

    def implements(*interfaces):
        """
        Make a base for a class that implements one or more interfaces.

        Parameters
        ----------
        *interfaces : tuple
            One or more subclasses of :class:`~interface.Interface`.

        Returns
        -------
        base : type
            A type validating that subclasses must implement all interface
            methods of types in ``interfaces``.

        Examples
        --------
        **Implementing an Interface:**

        .. code-block:: python

            class MyInterface(Interface):
                 def method1(self, x):
                     pass

                 def method2(self, y):
                     pass

            class MyImplementation(implements(MyInterface)):
                 def method1(self, x):
                     return x + 1

                 def method2(self, y):
                     return y * 2

        **Implementing Multiple Interfaces:**

        .. code-block:: python

            class I1(Interface):
                def method1(self, x):
                    pass

            class I2(Interface):
                def method2(self, y):
                    pass

            class ImplBoth(implements(I1, I2)):
                def method1(self, x):
                    return x + 1

                def method2(self, y):
                    return y * 2
        """
        if not interfaces:
            raise TypeError("implements() requires at least one interface")

        interfaces = frozenset(interfaces)
        try:
            return _memo[interfaces]
        except KeyError:
            pass

        for I in interfaces:
            if not issubclass(I, Interface):
                raise TypeError(
                    "implements() expected an Interface, but got %s." % I
                )

        ordered_ifaces = tuple(sorted(interfaces, key=getname))
        iface_names = list(map(getname, ordered_ifaces))

        name = "Implements{}".format("_".join(iface_names))
        doc = dedent(
            """\
            Implementation of {interfaces}.

            Methods
            -------
            {methods}"""
        ).format(
            interfaces=', '.join(iface_names),
            methods="\n".join(map(format_iface_method_docs, ordered_ifaces)),
        )

        result = ImplementsMeta(
            name,
            (object,),
            {'__doc__': doc},
            interfaces=interfaces,
        )

        # NOTE: It's important for correct weak-memoization that this is set is
        # stored somewhere on the resulting type.
        assert result._interfaces is interfaces, "Interfaces not stored."

        _memo[interfaces] = result
        return result
    return implements


implements = _make_implements()
del _make_implements
