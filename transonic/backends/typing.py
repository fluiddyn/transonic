normalized_types = {"float": "float64", "complex": "complex128"}


class TypeFormatter:
    def __init__(self, backend_name=None):
        self.backend_name = backend_name

    def normalize_type_name(self, name):
        try:
            return normalized_types[name]
        except KeyError:
            return name

    def make_array_code(self, dtype, ndim, memview):
        base = self.normalize_type_name(dtype.__name__)
        if ndim == 0:
            return base
        return base + f"[{', '.join(':'*ndim)}]"

    def make_dict_code(self, key, value):
        return f"{key}: {value} dict"


base_type_formatter = TypeFormatter()
