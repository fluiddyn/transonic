"""Pythran Backend
==================


"""

try:
    import black
except ImportError:
    black = False

from transonic.annotation import compute_pythran_types_from_valued_types

from .backend import BackendAOT


class PythranBackend(BackendAOT):
    backend_name = "pythran"
    suffix_header = ".pythran"

    def check_if_compiled(self, module):
        return hasattr(module, "__pythran__")

    def _make_header_1_function(self, func_name, fdef, annotations):

        signatures_func = set()
        try:
            ann = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            typess = compute_pythran_types_from_valued_types(ann.values())
            for types in typess:
                signatures_func.add(f"export {func_name}({', '.join(types)})")

        anns = annotations["__in_comments__"][func_name]
        if not fdef.args.args:
            signatures_func.add(f"export {func_name}()")
        for ann in anns:
            typess = compute_pythran_types_from_valued_types(ann.values())

            for types in typess:
                signatures_func.add(f"export {func_name}({', '.join(types)})")

        signatures_func = sorted(signatures_func)
        if signatures_func:
            signatures_func[-1] = signatures_func[-1] + "\n"
        return signatures_func
