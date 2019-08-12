"""Cython Backend
==================


"""
import copy
from textwrap import indent

from transonic.analyses import extast
from transonic.annotation import compute_pythran_types_from_valued_types
from transonic.util import format_str

from .backend import BackendAOT


class CythonBackend(BackendAOT):
    backend_name = "cython"

    def get_signatures(self, func_name, fdef, annotations):
        fdef2 = copy.deepcopy(fdef)
        signatures_func = []
        try:
            ann = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            # produce ctypedef
            typess = compute_pythran_types_from_valued_types(ann.values())
            index = 0
            name_args = []
            for arg in ann.keys():
                ctypedef = []
                name_arg = "__" + func_name + "_" + arg
                name_args.append(name_arg)
                ctypedef.append(f"ctypedef fused {name_arg}:\n")
                possible_types = [x[index] for x in typess]
                for possible_type in list(set(possible_types)):
                    ctypedef.append(f"   {possible_type}\n")
                index += 1
                signatures_func.append("".join(ctypedef))
            # change function parameters
            for name in fdef2.args.args:
                name.id = name_args[0] + " " + name.id
                del name_args[0]
        signatures_func.append(
            "cp"
            + self.get_code_function(fdef2, black=False)[2:].splitlines()[0][:-1]
            + "\n"
        )
        return signatures_func

    def get_code_blocks(self, blocks):
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

    def get_code_meths(self, boosted_dicts, annotations, path_py):
        meths_code = []
        signatures = []
        for (class_name, meth_name), fdef in boosted_dicts["methods"].items():

            signature, code_for_meth = self.get_code_meth(
                class_name, fdef, meth_name, annotations, boosted_dicts
            )
            meths_code.append(code_for_meth)
            signatures += signature
        return signatures, meths_code

    def get_code_meth(
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

        signature, code_for_meth = self.produce_code_for_method(
            fdef, class_def, annotations_meth, annotations_class
        )
        return signature, code_for_meth

    def produce_code_for_method(
        self, fdef, class_def, annotations_meth, annotations_class, jit=False
    ):

        signature = []
        class_name = class_def.name
        meth_name = fdef.name

        new_code, attributes, name_new_func = self.produce_new_code_method(
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
