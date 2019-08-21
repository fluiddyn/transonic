"""Pythran Backend
==================


"""

try:
    import black
except ImportError:
    black = False

from transonic.annotation import compute_signatures_from_typeobjects

from .backend import BackendAOT


class PythranBackend(BackendAOT):
    backend_name = "pythran"
    suffix_header = ".pythran"

    def check_if_compiled(self, module):
        return hasattr(module, "__pythran__")

    def _append_line_header_variable(self, lines_header, name_variable):
        lines_header.append(f"export {name_variable}\n")

    def _make_header_1_function(self, func_name, fdef, annotations):

        try:
            annots = annotations["__in_comments__"][func_name]
        except KeyError:
            annots = []

        try:
            annot = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            annots.append(annot)

        signatures_as_lists_strings = []
        for annot in annots:
            signatures_as_lists_strings.extend(
                compute_signatures_from_typeobjects(annot)
            )

        signatures_func = set()
        for signature_as_strings in signatures_as_lists_strings:
            signatures_func.add(
                f"export {func_name}({', '.join(signature_as_strings)})"
            )

        if not fdef.args.args and not signatures_func:
            signatures_func.add(f"export {func_name}()")

        signatures_func = sorted(signatures_func)
        if signatures_func:
            signatures_func[-1] = signatures_func[-1] + "\n"
        return signatures_func
