"""Cython Backend
=================

Internal API
------------

.. autoclass:: HeaderFunction
   :members:
   :private-members:

.. autoclass:: SubBackendJITCython
   :members:
   :private-members:

.. autoclass:: CythonBackend
   :members:
   :private-members:

"""
import copy
import inspect
from pprint import pprint
from warnings import warn
import itertools

from transonic.analyses.extast import unparse, ast
from transonic.annotation import (
    compute_pythran_type_from_type,
    make_signatures_from_typehinted_func,
)

from .base import BackendAOT, TypeHintRemover, format_str
from .base_jit import SubBackendJIT


def analyze_array_type(type_):
    """Analyze an array type. return dtype, ndim"""
    dtype, end = type_.split("[", 1)
    if not dtype.startswith("np."):
        dtype = "np." + dtype

    if ":" in end:
        ndim = end.count(":")
    else:
        ndim = end.count("[") + 1

    return dtype, ndim


def memoryview_type(type_) -> str:
    dtype, ndim = analyze_array_type(type_)

    if ndim > 1:
        end = "[" + ", ".join(":" * ndim) + "]"
    else:
        end = "[:]"

    return f"{dtype}_t{end}"


def np_ndarray_type(type_) -> str:
    dtype, ndim = analyze_array_type(type_)
    return f"np.ndarray[{dtype + '_t'}, ndim={ndim}]"


def compute_cython_type_from_pythran_type(type_, memoryview=False):

    if isinstance(type_, type):
        type_ = compute_pythran_type_from_type(type_)

    if type_.endswith("]"):
        if memoryview:
            return memoryview_type(type_)
        return np_ndarray_type(type_)

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


class SubBackendJITCython(SubBackendJIT):
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
    """Main class for the Cython backend"""

    backend_name = "cython"
    suffix_header = ".pxd"
    keyword_export = "cpdef"
    _SubBackendJIT = SubBackendJITCython

    def _make_first_lines_header(self):
        return ["import cython\n\nimport numpy as np\ncimport numpy as np\n"]

    def _future_make_header_from_fdef_annotations(
        self, fdef, annotations, locals_types=None, returns=None
    ):

        if hasattr(fdef, "_transonic_keywords"):
            decorator_keywords = fdef._transonic_keywords
        else:
            decorator_keywords = {}

        inline = decorator_keywords.get("inline", False)
        inline = "inline " if inline else ""

        fdef = ast.FunctionDef(
            name=fdef.name,
            args=copy.deepcopy(fdef.args),
            body=[],
            decorator_list=[],
            returns=None,
            type_comment=None,
        )

        assert isinstance(annotations, list)

        if len(annotations) > 1:
            warn(
                "Cython backend only support one set of annotations, "
                "but you can use fused types."
            )
        annotations = annotations[0]

        transonic_fused_types = set(annotations.values())

        if locals_types:
            transonic_fused_types.update(locals_types.values())

        if returns:
            transonic_fused_types.add(returns)

        pprint(transonic_fused_types)

        template_parameters = set()
        for type_ in transonic_fused_types:
            if hasattr(type_, "get_template_parameters"):
                template_parameters.update(type_.get_template_parameters())

        pprint(template_parameters)

        if not template_parameters:
            raise NotImplementedError

        if not all(param.values for param in template_parameters):
            raise ValueError(
                f"{template_parameters}, {[param.values for param in template_parameters]}"
            )

        cython_fused_types = {}

        for ttype in transonic_fused_types:
            name_cython_type = f"__{fdef.name}__{ttype.__name__}"
            cython_fused_types.setdefault(name_cython_type, [])
            template_params = ttype.get_template_parameters()
            names = [param.__name__ for param in template_params]
            values_template_parameters = {
                param.__name__: param.values for param in template_params
            }

            for set_types in itertools.product(
                *values_template_parameters.values()
            ):
                template_variables = dict(zip(names, set_types))
                cython_fused_types[name_cython_type].append(
                    compute_cython_type_from_pythran_type(
                        compute_pythran_type_from_type(
                            ttype, **template_variables
                        )
                    )
                )

        pprint(cython_fused_types)

        signatures_func = []

        for name, possible_types in cython_fused_types.items():
            ctypedef = [f"ctypedef fused {name}:\n"]
            for possible_type in sorted(set(possible_types)):
                ctypedef.append(f"   {possible_type}\n")
            signatures_func.append("".join(ctypedef))

        print("\n".join(signatures_func))

        # change function parameters
        if fdef.args.defaults:
            name_start = ast.Name("*", ast.Param(), None, None)
            fdef.args.defaults = [name_start] * len(fdef.args.defaults)
        for name in fdef.args.args:
            name.annotation = None
            ttype = annotations[name.id]
            name_cython_type = f"__{fdef.name}__{ttype.__name__}"
            name.id = f"{name_cython_type} {name.id}"

        def_keyword = "cpdef"

        if returns is not None:
            ttype = returns
            name_cython_type = f"__{fdef.name}__{ttype.__name__}"
            returns = name_cython_type + " "
        else:
            returns = ""

        signatures_func.append(
            f"{def_keyword} {inline}{returns}{unparse(fdef).strip()[4:-1]}\n"
        )
        return signatures_func

    def _make_header_from_fdef_signatures(
        self, fdef, signatures_as_lists_strings, locals_types=None, returns=None
    ):

        if hasattr(fdef, "_transonic_keywords"):
            decorator_keywords = fdef._transonic_keywords
        else:
            decorator_keywords = {}

        inline = decorator_keywords.get("inline", False)
        inline = "inline " if inline else ""

        fdef = ast.FunctionDef(
            name=fdef.name,
            args=copy.deepcopy(fdef.args),
            body=[],
            decorator_list=[],
            returns=None,
            type_comment=None,
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
            if fdef.args.defaults:
                name_start = ast.Name("*", ast.Param(), None, None)
                fdef.args.defaults = [name_start] * len(fdef.args.defaults)
            for name in fdef.args.args:
                name.annotation = None
                name.id = name_type_args[0] + " " + name.id
                del name_type_args[0]

        if locals_types is not None and locals_types:
            # TODO: fused types not supported here
            # note: np.ndarray not supported by Cython in "locals"
            locals_types = ", ".join(
                f"{k}={compute_cython_type_from_pythran_type(v, memoryview=True)}"
                for k, v in locals_types.items()
            )
            signatures_func.append(f"@cython.locals({locals_types})")

        def_keyword = "cpdef"

        if returns is not None:
            returns = compute_cython_type_from_pythran_type(returns) + " "
        else:
            returns = ""

        signatures_func.append(
            f"{def_keyword} {inline}{returns}{unparse(fdef).strip()[4:-1]}\n"
        )
        return signatures_func

    def _make_code_from_fdef_node(self, fdef):

        if hasattr(fdef, "_transonic_keywords"):
            decorator_keywords = fdef._transonic_keywords
        else:
            decorator_keywords = {}

        boundscheck = decorator_keywords.get("boundscheck", True)
        wraparound = decorator_keywords.get("wraparound", True)

        parts = []

        if not boundscheck:
            parts.append("@cython.boundscheck(False)")

        if not wraparound:
            parts.append("@cython.wraparound(False)")

        transformed = TypeHintRemover().visit(fdef)
        # convert the AST back to source code
        parts.append(unparse(transformed))

        return format_str("\n".join(parts))

    def _make_beginning_code(self):
        return (
            "try:\n"
            "    import cython\n"
            "except ImportError:\n"
            "    from transonic_cl import cython\n\n"
        )
