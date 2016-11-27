"""
Utilities for typed interfaces.
"""
from itertools import starmap, takewhile

from .compat import Parameter, zip_longest
from .functional import complement, dzip, valfilter


def compatible(impl_sig, iface_sig):
    """
    Check whether ``impl_sig`` is compatible with ``iface_sig``.

    Parameters
    ----------
    impl_sig : inspect.Signature
        The signature of the implementation function.
    iface_sig : inspect.Signature
        The signature of the interface function.

    In general, an implementation is compatible with an interface if any valid
    way of passing parameters to the interface method is also valid for the
    implementation.

    Consequently, the following differences are allowed between the signature
    of an implementation method and the signature of its interface definition:

    1. An implementation may add new arguments to an interface iff:
       a. All new arguments have default values.
       b. All new arguments accepted positionally (i.e. all non-keyword-only
          arguments) occur after any arguments declared by the interface.
       c. Keyword-only arguments may be reordered by the implementation.

    2. For type-annotated interfaces, type annotations my differ as follows:
       a. Arguments to implementations of an interface may be annotated with
          a **superclass** of the type specified by the interface.
       b. The return type of an implementation may be annotated with a
          **subclass** of the type specified by the interface.
    """
    return all([
        positionals_compatible(
            takewhile(is_positional, impl_sig.parameters.values()),
            takewhile(is_positional, iface_sig.parameters.values()),
        ),
        keywords_compatible(
            valfilter(complement(is_positional), impl_sig.parameters),
            valfilter(complement(is_positional), iface_sig.parameters),
        ),
    ])


_POSITIONALS = frozenset([
    Parameter.POSITIONAL_ONLY,
    Parameter.POSITIONAL_OR_KEYWORD,
])


def is_positional(arg):
    return arg.kind in _POSITIONALS


def has_default(arg):
    """
    Does ``arg`` provide a default?
    """
    return arg.default is not Parameter.empty


def params_compatible(impl, iface):

    if impl is None:
        return False

    if iface is None:
        return has_default(impl)

    return (
        impl.name == iface.name and
        impl.kind == iface.kind and
        has_default(impl) == has_default(iface) and
        annotations_compatible(impl, iface)
    )


def positionals_compatible(impl_positionals, iface_positionals):
    return all(
        starmap(params_compatible, zip_longest(impl_positionals, iface_positionals))
    )


def keywords_compatible(impl_keywords, iface_keywords):
    return all(
        starmap(params_compatible, dzip(impl_keywords, iface_keywords).values())
    )


def annotations_compatible(impl, iface):
    """
    Check whether the type annotations of an implementation are compatible with
    the annotations of the interface it implements.
    """
    return impl.annotation == iface.annotation
