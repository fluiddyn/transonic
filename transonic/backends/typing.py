normalized_types = {"float": "float64", "complex": "complex128"}


class TypeFormatter:
    def __init__(self, backend_name=None):
        self.backend_name = backend_name

    def normalize_type_name(self, name):
        if self.backend_name == "cython":
            return name

        try:
            return normalized_types[name]
        except KeyError:
            return name


base_type_formatter = TypeFormatter()
