"""Pythran Backend
==================

Internal API
------------

.. autoclass:: PythranBackend
   :members:
   :private-members:

"""

from .base import BackendAOT


class PythranBackend(BackendAOT):
    """Main class for the Pythran backend"""

    backend_name = "pythran"
    suffix_header = ".pythran"

    def check_if_compiled(self, module):
        return hasattr(module, "__pythran__")

    def _append_line_header_variable(self, lines_header, name_variable):
        lines_header.append(f"export {name_variable}\n")

    def _make_header_from_fdef_signatures(
        self, fdef, signatures_as_lists_strings, locals_types=None, returns=None
    ):
        nb_defaults = len(fdef.args.defaults)
        if nb_defaults:
            new_signatures = []
            for signature_as_strings in signatures_as_lists_strings:
                for nb_args_not_given in range(1, nb_defaults + 1):
                    new_signatures.append(
                        signature_as_strings[:-nb_args_not_given]
                    )
            signatures_as_lists_strings.extend(new_signatures)

        signatures_func = set(
            f"export {fdef.name}({', '.join(signature_as_strings)})"
            for signature_as_strings in signatures_as_lists_strings
        )

        if not fdef.args.args and not signatures_func:
            signatures_func.add(f"export {fdef.name}()")

        signatures_func = sorted(signatures_func)
        if signatures_func:
            signatures_func[-1] = signatures_func[-1] + "\n"
        return signatures_func
