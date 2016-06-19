"""
interface
---------
"""
from functools import wraps
import inspect
from operator import itemgetter
from textwrap import dedent
from weakref import WeakKeyDictionary

first = itemgetter(0)


def compatible(meth_sig, iface_sig):
    """
    Check if ``method``'s signature is compatible with ``signature``.
    """
    # TODO: Allow method to provide defaults and optional extensions to
    # ``signature``.
    return meth_sig == iface_sig


def strict_issubclass(t, parent):
    return issubclass(t, parent) and t is not parent


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
            f_sig = inspect.signature(f)
            if not compatible(f_sig, iface_sig):
                mismatched[name] = f_sig
        return missing, mismatched

    def check_conforms(self, type_):
        """
        Check whether a type implements our interface.

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
            C=t.__name__,
            I=self.__name__,
        )
        if missing:
            message += dedent(
                """

                The following methods were not implemented:
                {missing_methods}"""
            ).format(missing_methods=self._format_missing_methods(missing))

        if mismatched:
            message += (
                "\n\nThe following methods were implemented but had invalid"
                " signatures:\n"
                "{mismatched_methods}"
            ).format(
                mismatched_methods=self._format_mismatched_methods(mismatched),
            )
        return TypeError(message)

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


class Implements:
    """
    Base class for an implementation of an interface.
    """


class ImplementsMeta(type):
    """
    Metaclass for implementations of particular interfaces.
    """
    def __new__(mcls, name, bases, clsdict, base=False):
        newtype = super().__new__(mcls, name, bases, clsdict)

        if base:
            # Don't do checks on the types returned by ``implements``.
            return newtype

        for iface in newtype.interfaces():
            iface.check_conforms(newtype)

        return newtype

    def __init__(mcls, name, bases, clsdict, base=False):
        super().__init__(name, bases, clsdict)

    def interfaces(self):
        """
        Return a generator of interfaces implemented by this type.

        Yields
        ------
        iface : Interface
        """
        for base in self.mro():
            if strict_issubclass(base, Implements):
                yield base.interface


def weakmemoize_implements(f):
    "One-off weakmemoize implementation for ``implements``."
    _memo = WeakKeyDictionary()

    @wraps(f)
    def _f(I):
        try:
            return _memo[I]
        except KeyError:
            pass
        ret = f(I)
        _memo[I] = ret
        return ret
    return _f


@weakmemoize_implements
def implements(I):
    """
    Make a base for classes that implement ``I``.

    Parameters
    ----------
    I : Interface

    Returns
    -------
    base : type
        A type validating that subclasses must implement all interface
        methods of I.
    """
    if not issubclass(I, Interface):
        raise TypeError(
            "implements() expected an Interface, but got %s." % I
        )

    name = "Implements{I}".format(I=I.__name__)
    doc = dedent(
        """\
        Implementation of {I}.

        Methods
        -------
        {methods}"""
    ).format(
        I=I.__name__,
        methods="\n".join(
            "{name}{sig}".format(name=name, sig=sig)
            for name, sig in sorted(list(I._signatures.items()), key=first)
        )
    )
    return ImplementsMeta(
        name,
        (Implements,),
        {'__doc__': doc, 'interface': I},
        base=True,
    )
