import dis
import warnings

from .compat import PY3
from .formatting import bulleted_list
from .functional import keysorted, sliding_window


class default(object):
    """Default implementation of a function in terms of interface methods.
    """
    def __init__(self, implementation):
        self.implementation = implementation

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.implementation)


class UnsafeDefault(UserWarning):
    pass


if PY3:  # pragma: nocover-py2
    _DEFAULT_USES_NON_INTERFACE_MEMBER_TEMPLATE = (
        "Default for {iface}.{method} uses non-interface attributes.\n\n"
        "The following attributes are used but are not part of "
        "the interface:\n"
        "{non_members}\n\n"
        "Consider changing {iface}.{method} or making these attributes"
        " part of {iface}."
    )

    def warn_if_defaults_use_non_interface_members(interface_name,
                                                   defaults,
                                                   members):
        """Warn if an interface default uses non-interface members of self.
        """
        for method_name, attrs in non_member_attributes(defaults, members):
            warnings.warn(_DEFAULT_USES_NON_INTERFACE_MEMBER_TEMPLATE.format(
                iface=interface_name,
                method=method_name,
                non_members=bulleted_list(attrs),
            ), category=UnsafeDefault, stacklevel=3)

    def non_member_attributes(defaults, members):
        from .typed_signature import TypedSignature

        for default_name, default in keysorted(defaults):
            impl = default.implementation

            if isinstance(impl, staticmethod):
                # staticmethods can't use attributes of the interface.
                continue

            self_name = TypedSignature(impl).first_argument_name
            if self_name is None:
                # No parameters.
                # TODO: This is probably a bug in the interface, since a method
                # with no parameters that's not a staticmethod probably can't
                # be called in any natural way.
                continue

            used = accessed_attributes_of_local(impl, self_name)
            non_interface_usages = used - members

            if non_interface_usages:
                yield default_name, sorted(non_interface_usages)

    def accessed_attributes_of_local(f, local_name):
        """
        Get a list of attributes of ``local_name`` accessed by ``f``.

        The analysis performed by this function is conservative, meaning that
        it's not guaranteed to find **all** attributes used.
        """
        used = set()
        # Find sequences of the form: LOAD_FAST(local_name), LOAD_ATTR(<name>).
        # This will find all usages of the form ``local_name.<name>``.
        #
        # It will **NOT** find usages in which ``local_name`` is aliased to
        # another name.
        for first, second in sliding_window(dis.get_instructions(f), 2):
            if first.opname == 'LOAD_FAST' and first.argval == local_name:
                if second.opname in ('LOAD_ATTR', 'LOAD_METHOD', 'STORE_ATTR'):
                    used.add(second.argval)
        return used

else:  # pragma: nocover-py3
    def warn_if_defaults_use_non_interface_members(*args, **kwargs):
        pass

    def non_member_warnings(*args, **kwargs):
        return iter(())

    def accessed_attributes_of_local(*args, **kwargs):
        return set()
