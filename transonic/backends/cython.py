"""Cython Backend
==================


"""
import copy
from textwrap import indent

from transonic.analyses import extast
from transonic.annotation import (
    compute_pythran_types_from_valued_types,
    compute_pythran_type_from_type,
)
from transonic.util import format_str

from .backend import BackendAOT


def compute_cython_type_from_pythran_type(type_):

    if isinstance(type_, type):
        type_ = compute_pythran_type_from_type(type_)

    if type_.endswith("]"):
        start, end = type_.split("[")
        if not start.startswith("np."):
            start = "np." + start
        return start + "_t[" + end

    if any(type_.endswith(str(number)) for number in (32, 64, 128)):
        return "np." + type_

    return "cython." + type_


class CythonBackend(BackendAOT):
    backend_name = "cython"
    suffix_header = ".pxd"

    def _make_signatures_1_function(self, func_name, fdef, annotations):
        fdef = copy.deepcopy(fdef)
        signatures_func = []
        try:
            annot = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            # produce ctypedef
            typess = compute_pythran_types_from_valued_types(annot.values())
            index = 0
            name_type_args = []
            for arg in annot.keys():
                ctypedef = []
                name_type_arg = "__" + func_name + "_" + arg
                name_type_args.append(name_type_arg)
                ctypedef.append(f"ctypedef fused {name_type_arg}:\n")
                possible_types = [x[index] for x in typess]
                for possible_type in list(set(possible_types)):
                    ctypedef.append(
                        f"   {compute_cython_type_from_pythran_type(possible_type)}\n"
                    )
                index += 1
                signatures_func.append("".join(ctypedef))
            # change function parameters
            for name in fdef.args.args:
                name.annotation = None
                name.id = name_type_args[0] + " " + name.id
                del name_type_args[0]

        fdef.body = []
        fdef.decorator_list = []
        try:
            locals_types = annotations["__locals__"][func_name]
        except KeyError:
            pass
        else:
            locals_types = ", ".join(
                f"{k}={compute_cython_type_from_pythran_type(v)}"
                for k, v in locals_types.items()
            )
            signatures_func.append(f"@cython.locals({locals_types})\n")

        signatures_func.append("cp" + extast.unparse(fdef).strip()[:-1] + "\n")
        return signatures_func

    def _make_code_blocks(self, blocks):
        code = []
        signatures = []
        for block in blocks:
            signatures_block = set()
            for ann in block.signatures:
                typess = compute_pythran_types_from_valued_types(ann.values())

                for types in typess:
                    signatures_block.add(
                        f"cpdef {block.name}({', '.join(types)})\n"
                    )

            signatures.extend(sorted(signatures_block))

            str_variables = ", ".join(block.signatures[0].keys())

            code.append(f"\ndef {block.name}({str_variables}):\n")

            code_block = indent(extast.unparse(block.ast_code), "    ")

            code.append(code_block)

            if block.results:
                code.append(f"    return {', '.join(block.results)}\n")

        arguments_blocks = {
            block.name: list(block.signatures[0].keys()) for block in blocks
        }

        # TODO do something with argument blocks ?
        if arguments_blocks:
            code.append(f"arguments_blocks = {str(arguments_blocks)}\n")

        return signatures, code

    def _make_code_methods(self, boosted_dicts, annotations, path_py):
        meths_code = []
        signatures = []
        for (class_name, meth_name), fdef in boosted_dicts["methods"].items():

            signature, code_for_meth = self._make_code_method(
                class_name, fdef, meth_name, annotations, boosted_dicts
            )
            meths_code.append(code_for_meth)
            signatures += signature
        return signatures, meths_code

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

        signature, code_for_meth = self._make_code_for_method(
            fdef, class_def, annotations_meth, annotations_class
        )
        return signature, code_for_meth

    def _make_code_for_method(
        self, fdef, class_def, annotations_meth, annotations_class, jit=False
    ):

        signature = []
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
                f"cpdef {name_new_func}({', '.join(types_string_signature)})\n"
            )

        if jit:
            new_code = "from transonic import jit\n\n@jit\n" + new_code

        signature.append("\n".join(sorted(pythran_signatures)) + "\n")
        python_code = new_code

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
                f'\n{name_var_code_new_method} = """\n\n'
                f"def new_method(self, {str_args_value_func}):\n"
                f"    return backend_func({str_args_backend_func})"
                '\n\n"""\n'
            )

        python_code = format_str(python_code)

        return signature, python_code
