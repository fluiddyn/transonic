"""Cython Backend
==================


"""
import copy
import inspect

from transonic.analyses import extast
from transonic.annotation import (
    compute_pythran_type_from_type,
    make_signatures_from_typehinted_func,
)

from .base import BackendAOT
from .base_jit import SubBackendJIT


def compute_cython_type_from_pythran_type(type_):

    if isinstance(type_, type):
        type_ = compute_pythran_type_from_type(type_)

    if type_.endswith("]"):
        start, end = type_.split("[", 1)
        if not start.startswith("np."):
            start = "np." + start

        dim = end.count("[") + 1
        if dim > 1:
            end = ",".join(":" * dim) + "]"

        if end == "]":
            end = ":]"

        return start + "_t[" + end

    if any(type_.endswith(str(number)) for number in (32, 64, 128)):
        return "np." + type_ + "_t"

    if "dict" in type_:
        return "dict"

    return "cython." + type_


class HeaderFunction:
    def __init__(
        self,
        path=None,
        name=None,
        arguments=None,
        types: dict = None,
        imports=None,
    ):

        if path is not None:
            self.path = path
            with open(path) as file:
                lines = file.readlines()

            last_line = lines[-1]
            assert last_line.startswith("cpdef ")
            name = last_line.split(" ", 1)[1].split("(", 1)[0]

            parts = [
                part.strip()
                for part in "".join(lines[:-1]).split("ctypedef fused ")
            ]
            imports = parts[0]

            types = {}

            for part in parts[1:]:
                assert part.startswith(f"__{name}_")
                lines = part.split("\n")
                arg_name = lines[0].split(f"__{name}_", 1)[1].split(":", 1)[0]
                types[arg_name] = set(line.strip() for line in lines[1:])

        if types is None:
            if arguments is None:
                raise ValueError
            types = {key: set() for key in arguments}

        if arguments is None:
            arguments = types.keys()

        self.arguments = arguments
        self.name = name
        self.types = types
        self.imports = imports

    def make_code(self):

        bits = [self.imports + "\n\n"]

        for arg, types in self.types.items():
            bits.append(f"ctypedef fused __{self.name}_{arg}:\n")
            for type_ in sorted(types):
                bits.append(f"    {type_}\n")
            bits.append("\n")

        tmp = ", ".join(f"__{self.name}_{arg} {arg}" for arg in self.types)
        bits.append(f"cpdef {self.name}({tmp})")
        code = "".join(bits)
        return code

    def add_signature(self, new_types):
        for new_type, set_types in zip(new_types, self.types.values()):
            set_types.add(new_type)

    def update_with_other_header(self, other):
        if self.name != other.name:
            raise ValueError
        if self.types.keys() != other.types.keys():
            raise ValueError
        for key, value in other.types.items():
            self.types[key].update(value)


class SubCythonJIT(SubBackendJIT):
    def compute_typename_from_object(self, obj: object):
        """return the Pythran type name"""
        return compute_cython_type_from_pythran_type(
            super().compute_typename_from_object(obj)
        )

    def make_new_header(self, func, arg_types):
        # Include signature comming from type hints
        header = HeaderFunction(
            name=func.__name__,
            arguments=list(inspect.signature(func).parameters.keys()),
            imports="import cython\n\nimport numpy as np\ncimport numpy as np\n",
        )

        signatures = make_signatures_from_typehinted_func(func, as_list_str=True)

        for signature in signatures:
            header.add_signature(
                compute_cython_type_from_pythran_type(type_)
                for type_ in signature
            )

        if arg_types != "no types":
            header.add_signature(arg_types)

        return header

    def _load_old_header(self, path_backend_header):
        return HeaderFunction(path=path_backend_header)

    def _merge_header_objects(self, header, header_old):
        header.update_with_other_header(header_old)
        return header

    def _make_header_code(self, header):
        return header.make_code()


class CythonBackend(BackendAOT):
    backend_name = "cython"
    suffix_header = ".pxd"
    keyword_export = "cpdef"
    _SubBackendJIT = SubCythonJIT

    def _make_first_lines_header(self):
        return ["import cython\n\nimport numpy as np\ncimport numpy as np\n"]

    def _make_header_from_fdef_signatures(
        self, fdef, signatures_as_lists_strings, locals_types=None
    ):

        fdef = extast.ast.FunctionDef(
            name=fdef.name,
            args=copy.deepcopy(fdef.args),
            body=[],
            decorator_list=[],
            returns=None,
        )
        signatures_func = []
        if signatures_as_lists_strings:
            # produce ctypedef
            index = 0
            name_type_args = []
            for arg in [name.id for name in fdef.args.args]:
                ctypedef = []
                name_type_arg = f"__{fdef.name}_{arg}"
                name_type_args.append(name_type_arg)
                ctypedef.append(f"ctypedef fused {name_type_arg}:\n")
                possible_types = [x[index] for x in signatures_as_lists_strings]
                for possible_type in sorted(set(possible_types)):
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

        if locals_types is not None and locals_types:
            # TODO: fused types not supported here
            locals_types = ", ".join(
                f"{k}={compute_cython_type_from_pythran_type(v)}"
                for k, v in locals_types.items()
            )
            signatures_func.append(f"@cython.locals({locals_types})\n")

        signatures_func.append("cp" + extast.unparse(fdef).strip()[:-1] + "\n")
        return signatures_func
