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

from warnings import warn

from transonic.analyses.extast import unparse, gast, FunctionDef, Name
from transonic.signatures import make_signatures_from_typehinted_func
from transonic.typing import format_type_as_backend_type, MemLayout

from .base import BackendAOT, TypeHintRemover, format_str
from .base_jit import SubBackendJIT
from .typing import TypeFormatter


def normalize_type_name_for_array(name):
    if name == "bool_":
        return "np.uint8"
    if any(name.endswith(str(number)) for number in (8, 16, 32, 64, 128)):
        return "np." + name
    if name in ("int", "float", "complex"):
        return "np." + name
    return name


class TypeFormatterCython(TypeFormatter):
    def normalize_type_name(self, name):
        if any(name.endswith(str(number)) for number in (8, 16, 32, 64, 128)):
            return "np." + name + "_t"
        if name in ("int", "float", "complex", "str"):
            return f"cython.{name}"
        return name

    def make_array_code(
        self, dtype, ndim, shape, memview, mem_layout, positive_indices
    ):
        dtype = normalize_type_name_for_array(dtype.__name__)
        if ndim == 0:
            return dtype

        if memview:
            return memoryview_type(dtype, ndim, mem_layout)
        else:
            return np_ndarray_type(dtype, ndim, mem_layout, positive_indices)

    def make_dict_code(self, type_keys, type_values, **kwargs):
        return "dict"

    def make_set_code(self, type_keys, **kwargs):
        return "set"

    def make_list_code(self, type_elem, **kwargs):
        return "list"

    def make_tuple_code(self, types, **kwargs):
        return "tuple"

    def make_const_code(self, code):
        return "const " + code


def memoryview_type(dtype, ndim, mem_layout) -> str:
    ndim_F = 0
    ndim_C = 0
    if mem_layout is MemLayout.C:
        ndim_C = 1
        ndim -= 1
    elif mem_layout is MemLayout.F:
        ndim_F = 1
        ndim -= 1
    end = ", ".join(["::1"] * ndim_F + [":"] * ndim + ["::1"] * ndim_C)
    return f"{dtype}_t[{end}]"


def np_ndarray_type(dtype, ndim, mem_layout, positive_indices) -> str:
    if mem_layout is MemLayout.C:
        mode = ', mode="c"'
    elif mem_layout is MemLayout.F:
        mode = ', mode="f"'
    else:
        mode = ""

    if positive_indices:
        positive_indices = ", negative_indices=False"
    else:
        positive_indices = ""

    return f"np.ndarray[{dtype}_t, ndim={ndim}{mode}{positive_indices}]"


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
    def make_new_header(self, func, arg_types):
        # Include signature comming from type hints
        header = HeaderFunction(
            name=func.__name__,
            arguments=list(inspect.signature(func).parameters.keys()),
            imports="import cython\n\nimport numpy as np\ncimport numpy as np\n",
        )

        signatures = make_signatures_from_typehinted_func(
            func, self.type_formatter, as_list_str=True
        )

        for signature in signatures:
            header.add_signature(signature)

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
    _TypeFormatter = TypeFormatterCython

    def _make_first_lines_header(self):
        return ["import cython\n\nimport numpy as np\ncimport numpy as np\n"]

    def _make_header_from_fdef_annotations(
        self, fdef, annotations: dict, locals_types=None, returns=None
    ):

        if hasattr(fdef, "_transonic_keywords"):
            decorator_keywords = fdef._transonic_keywords
        else:
            decorator_keywords = {}

        inline = decorator_keywords.get("inline", False)
        inline = "inline " if inline else ""

        fdef = FunctionDef(name=fdef.name, args=copy.deepcopy(fdef.args), body=[])

        assert isinstance(annotations, list)

        if len(annotations) > 1:
            warn(
                "Cython backend only supports one set of annotations. "
                "Please use Transonic fused types."
            )

        try:
            annotations = annotations[0]
        except IndexError:
            annotations = {}

        transonic_types = set(annotations.values())

        if locals_types:
            transonic_types.update(locals_types.values())

        if returns:
            transonic_types.add(returns)

        transonic_types = sorted(transonic_types, key=repr)

        template_parameters = set()
        for ttype in transonic_types:
            if hasattr(ttype, "get_template_parameters"):
                template_parameters.update(ttype.get_template_parameters())

        template_parameters = sorted(template_parameters, key=repr)

        transonic_fused_types = [
            ttype
            for ttype in transonic_types
            if hasattr(ttype, "is_fused_type") and ttype.is_fused_type()
        ]

        if not all(param.values for param in template_parameters):
            raise ValueError(
                f"{template_parameters}, {[param.values for param in template_parameters]}"
            )

        cython_fused_types = {}

        def get_ttype_name(ttype):
            if hasattr(ttype, "short_repr"):
                ttype_name = ttype.short_repr()
            elif hasattr(ttype, "__name__"):
                ttype_name = ttype.__name__
            elif isinstance(ttype, str):
                ttype_name = ttype
            else:
                raise RuntimeError
            return ttype_name

        for ttype in transonic_fused_types:
            ttype_name = get_ttype_name(ttype)
            name_cython_type = f"__{fdef.name}__{ttype_name}"

            cython_types = ttype.get_all_formatted_backend_types(
                self.type_formatter
            )
            if "None" in cython_types:
                cython_types.remove("None")
            cython_fused_types[name_cython_type] = cython_types

        signatures_func = []

        for name, possible_types in cython_fused_types.items():
            ctypedef = [f"ctypedef fused {name}:\n"]
            for possible_type in sorted(set(possible_types)):
                ctypedef.append(f"   {possible_type}\n")
            signatures_func.append("".join(ctypedef))

        def get_name_cython_type(ttype):
            ttype_name = get_ttype_name(ttype)
            name_cython_type = f"__{fdef.name}__{ttype_name}"
            if name_cython_type in cython_fused_types:
                return name_cython_type
            return format_type_as_backend_type(ttype, self.type_formatter)

        # change function parameters
        if fdef.args.defaults:
            name_start = Name("*", gast.Param())
            fdef.args.defaults = [name_start] * len(fdef.args.defaults)
        for name in fdef.args.args:
            name.annotation = None
            if annotations:
                ttype = annotations[name.id]
                name_cython_type = get_name_cython_type(ttype)
            else:
                name_cython_type = "object"
            name.id = f"{name_cython_type} {name.id}"

        if locals_types is not None and locals_types:
            # note: np.ndarray not supported by Cython in "locals"
            # TODO: thus, fused types not supported here
            locals_types = ", ".join(
                f"{k}={format_type_as_backend_type(v, self.type_formatter, memview=True)}"
                for k, v in locals_types.items()
            )
            signatures_func.append(f"@cython.locals({locals_types})")

        if returns is not None:
            ttype = returns
            name_cython_type = get_name_cython_type(ttype)
            returns = name_cython_type + " "
        else:
            returns = ""

        def_keyword = "cpdef"
        signatures_func.append(
            f"{def_keyword} {inline}{returns}{unparse(fdef).strip()[4:-1]}\n"
        )
        return signatures_func

    def _make_code_from_fdef_node(self, fdef):

        if hasattr(fdef, "_transonic_keywords"):
            decorator_keywords = fdef._transonic_keywords
        else:
            decorator_keywords = {}

        parts = []

        if not decorator_keywords.get("boundscheck", True):
            parts.append("@cython.boundscheck(False)")

        if not decorator_keywords.get("wraparound", True):
            parts.append("@cython.wraparound(False)")

        if decorator_keywords.get("cdivision", False):
            parts.append("@cython.cdivision(True)")

        if not decorator_keywords.get("nonecheck", True):
            parts.append("@cython.noneckeck(False)")

        if decorator_keywords.get("nogil", False):
            parts.append("@cython.nogil")

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
