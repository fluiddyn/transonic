from transonic.typing import format_type_as_backend_type, MemLayout

normalized_types = {"float": "float64", "complex": "complex128", "bool_": "bool"}


class TypeFormatter:
    def __init__(self, backend_name=None):
        self.backend_name = backend_name

    def normalize_type_name(self, name):
        try:
            return normalized_types[name]
        except KeyError:
            return name

    def make_array_code(
        self, dtype, ndim, shape, memview, mem_layout, positive_indices
    ):
        dtype = self.normalize_type_name(dtype.__name__)
        if ndim == 0:
            return dtype
        one_dim = [":"]
        if mem_layout is MemLayout.strided:
            one_dim = ["::"]
        for_shape = one_dim * ndim
        if shape is not None:
            assert ndim == len(shape)
            for index, value in enumerate(shape):
                if value is not None:
                    for_shape[index] = str(value)
        result = f"{dtype}[{', '.join(for_shape)}]"
        if mem_layout is MemLayout.C:
            result += " order(C)"
        elif mem_layout is MemLayout.F:
            result += " order(F)"
        return result

    def make_dict_code(self, type_keys, type_values, **kwargs):
        key = format_type_as_backend_type(type_keys, self, **kwargs)
        value = format_type_as_backend_type(type_values, self, **kwargs)
        return f"{key}: {value} dict"

    def make_set_code(self, type_keys, **kwargs):
        key = format_type_as_backend_type(type_keys, self, **kwargs)
        return f"{key} set"

    def make_list_code(self, type_elem, **kwargs):
        return format_type_as_backend_type(type_elem, self, **kwargs) + " list"

    def make_tuple_code(self, types, **kwargs):
        strings = [
            format_type_as_backend_type(type_, self, **kwargs) for type_ in types
        ]
        return f"({', '.join(strings)})"

    def make_const_code(self, code):
        return code


base_type_formatter = TypeFormatter()
