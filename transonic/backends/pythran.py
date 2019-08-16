"""Pythran Backend
==================


"""

try:
    import black
except ImportError:
    black = False

from transonic.analyses import extast
from transonic.annotation import compute_pythran_types_from_valued_types
from transonic.util import format_str

from .backend import BackendAOT


class PythranBackend(BackendAOT):
    backend_name = "pythran"

    def check_if_compiled(self, module):
        return hasattr(module, "__pythran__")

    def _make_signatures_1_function(self, func_name, fdef, annotations):

        signatures_func = set()
        try:
            ann = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            typess = compute_pythran_types_from_valued_types(ann.values())
            for types in typess:
                signatures_func.add(
                    f"# pythran export {func_name}({', '.join(types)})"
                )

        anns = annotations["__in_comments__"][func_name]
        if not fdef.args.args:
            signatures_func.add(f"# pythran export {func_name}()")
        for ann in anns:
            typess = compute_pythran_types_from_valued_types(ann.values())

            for types in typess:
                signatures_func.add(
                    f"# pythran export {func_name}({', '.join(types)})"
                )
        return signatures_func

    def _make_code_methods(self, boosted_dicts, annotations, path_py):
        meths_code = []
        for (class_name, meth_name), fdef in boosted_dicts["methods"].items():

            code_for_meth = self._make_code_method(
                class_name, fdef, meth_name, annotations, boosted_dicts
            )
            meths_code.append(code_for_meth)
        return "", meths_code

    def _make_code_method(
        self, class_name, fdef, meth_name, annotations, boosted_dicts
    ):
        class_def = boosted_dicts["classes"][class_name]

        if class_name in annotations["classes"]:
            annotations_class = annotations["classes"][class_name]
        else:
            annotations_class = {}

        if (class_name, meth_name) in annotations["methods"]:
            annotations_meth = annotations["methods"][(class_name, meth_name)]
        else:
            annotations_meth = {}

        code_for_meth = self._make_code_for_method(
            fdef, class_def, annotations_meth, annotations_class
        )
        return code_for_meth

    def _make_code_for_method(
        self, fdef, class_def, annotations_meth, annotations_class, jit=False
    ):

        class_name = class_def.name
        meth_name = fdef.name

        new_code, attributes, name_new_func = self._make_new_code_method(
            fdef, class_def
        )

        types_attrs = []

        for attr in attributes:
            if attr not in annotations_class:
                raise NotImplementedError(
                    f"self.{attr} used but {attr} not in class annotations"
                )
        types_attrs = [annotations_class[attr] for attr in attributes]

        types_func = list(annotations_meth.values())

        types_pythran = types_attrs + types_func

        try:
            types_string_signatures = compute_pythran_types_from_valued_types(
                types_pythran
            )
        except ValueError:
            if jit:
                types_string_signatures = []
            else:
                raise

        pythran_signatures = set()

        for types_string_signature in types_string_signatures:
            pythran_signatures.add(
                "# pythran export "
                + name_new_func
                + "("
                + ", ".join(types_string_signature)
                + ")\n"
            )

        if jit:
            new_code = "from transonic import jit\n\n@jit\n" + new_code

        python_code = "\n".join(sorted(pythran_signatures)) + "\n" + new_code

        str_self_dot_attributes = ", ".join("self." + attr for attr in attributes)
        args_func = [arg.id for arg in fdef.args.args[1:]]
        str_args_func = ", ".join(args_func)

        defaults = fdef.args.defaults
        nb_defaults = len(defaults)
        nb_args = len(fdef.args.args)
        nb_no_defaults = nb_args - nb_defaults - 1

        str_args_value_func = []
        ind_default = 0
        for ind, arg in enumerate(fdef.args.args[1:]):
            name = arg.id
            if ind < nb_no_defaults:
                str_args_value_func.append(f"{name}")
            else:
                default = extast.unparse(defaults[ind_default]).strip()
                str_args_value_func.append(f"{name}={default}")
                ind_default += 1

        str_args_value_func = ", ".join(str_args_value_func)

        if str_self_dot_attributes:
            str_args_backend_func = ", ".join(
                (str_self_dot_attributes, str_args_func)
            )
        else:
            str_args_backend_func = str_args_func

        if jit:
            name_new_method = f"__new_method__{class_name}__{meth_name}"
            python_code += (
                f"\ndef {name_new_method}"
                f"(self, {str_args_value_func}):\n"
                f"    return {name_new_func}({str_args_backend_func})"
                "\n"
            )
        else:
            name_var_code_new_method = (
                f"__code_new_method__{class_name}__{meth_name}"
            )
            python_code += (
                f"\n# pythran export {name_var_code_new_method}\n"
                f'\n{name_var_code_new_method} = """\n\n'
                f"def new_method(self, {str_args_value_func}):\n"
                f"    return backend_func({str_args_backend_func})"
                '\n\n"""\n'
            )

        python_code = format_str(python_code)

        return python_code
