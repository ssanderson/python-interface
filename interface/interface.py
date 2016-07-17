"""
interface
---------
"""
from functools import wraps
import inspect
from operator import attrgetter, itemgetter
from textwrap import dedent
from weakref import WeakKeyDictionary

from .typecheck import compatible
from .utils import is_a, unique

first = itemgetter(0)
getname = attrgetter('__name__')


class IncompleteImplementation(TypeError):
    """
    Raised when a class intending to implement an interface fails to do so.
    """


class InterfaceMeta(type):
    """
    Metaclass for interfaces.

    Supplies a ``_signatures`` attribute and a ``check_implementation`` method.
    """
    def __new__(mcls, name, bases, clsdict):
        signatures = {}
        for k, v in clsdict.items():
            try:
                signatures[k] = inspect.signature(v)
            except TypeError:
                pass

        clsdict['_signatures'] = signatures
        return super().__new__(mcls, name, bases, clsdict)

    def _diff_signatures(self, type_):
        """
        Diff our method signatures against the methods provided by type_.

        Parameters
        ----------
        type_ : type
           The type to check.

        Returns
        -------
        missing, mismatched : list[str], dict[str -> signature]
            ``missing`` is a list of missing method names.
            ``mismatched`` is a dict mapping method names to incorrect
            signatures.
        """
        missing = []
        mismatched = {}
        for name, iface_sig in self._signatures.items():
            try:
                f = getattr(type_, name)
            except AttributeError:
                missing.append(name)
                continue
            impl_sig = inspect.signature(f)
            if not compatible(impl_sig, iface_sig):
                mismatched[name] = impl_sig
        return missing, mismatched

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
        missing, mismatched = self._diff_signatures(type_)
        if not missing and not mismatched:
            return
        raise self._invalid_implementation(type_, missing, mismatched)

    def _invalid_implementation(self, t, missing, mismatched):
        """
        Make a TypeError explaining why ``t`` doesn't implement our interface.
        """
        assert missing or mismatched, "Implementation wasn't invalid."

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

        if mismatched:
            message += dedent(
                """

                The following methods of {I} were implemented with invalid signatures:
                {mismatched_methods}"""
            ).format(
                I=getname(self),
                mismatched_methods=self._format_mismatched_methods(mismatched),
            )
        return IncompleteImplementation(message)

    def _format_missing_methods(self, missing):
        return "\n".join(sorted([
            "  - {name}{sig}".format(name=name, sig=self._signatures[name])
            for name in missing
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


class Interface(metaclass=InterfaceMeta):
    """
    Base class for interface definitions.
    """
    def __new__(cls, *args, **kwargs):
        raise TypeError("Can't instantiate interface %s" % getname(cls))


empty_set = frozenset([])


class ImplementsMeta(type):
    """
    Metaclass for implementations of particular interfaces.
    """
    def __new__(mcls, name, bases, clsdict, interfaces=empty_set):
        assert isinstance(interfaces, frozenset)

        newtype = super().__new__(mcls, name, bases, clsdict)

        if interfaces:
            # Don't do checks on the types returned by ``implements``.
            return newtype

        errors = []
        for iface in newtype.interfaces():
            try:
                iface.verify(newtype)
            except IncompleteImplementation as e:
                errors.append(e)

        if not errors:
            return newtype
        elif len(errors) == 1:
            raise errors[0]
        else:
            raise IncompleteImplementation("\n\n".join(map(str, errors)))

    def __init__(mcls, name, bases, clsdict, interfaces=empty_set):
        mcls._interfaces = interfaces
        super().__init__(name, bases, clsdict)

    def interfaces(self):
        yield from unique(self._interfaces_with_duplicates())

    def _interfaces_with_duplicates(self):
        yield from self._interfaces
        for t in filter(is_a(ImplementsMeta), self.mro()):
            yield from t._interfaces


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
        Make a base for classes that implement ``*interfaces``.

        Parameters
        ----------
        I : Interface

        Returns
        -------
        base : type
            A type validating that subclasses must implement all interface
            methods of I.
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

        name = "Implements{I}".format(I="_".join(iface_names))
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
