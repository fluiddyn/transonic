"""Compute function signatures
==============================

Internal API
------------

.. autofunction:: _format_types_as_backend_types

.. autofunction:: compute_signatures_from_typeobjects

.. autofunction:: _make_signature_from_template_variables

.. autofunction:: make_signatures_from_typehinted_func

"""

import itertools
import inspect
from typing import List

from transonic.typing import format_type_as_backend_type, str2type


def _format_types_as_backend_types(types, backend_type_formatter, **kwargs):
    """Compute a list of pythran types

    """
    backend_types = []
    for type_ in types:
        backend_types.append(
            format_type_as_backend_type(type_, backend_type_formatter, **kwargs)
        )

    # TODO: handle this with an exception
    if "_empty" in backend_types:
        raise ValueError(
            "At least one annotation type lacking in a signature.\n"
            f"types = {types}"
        )

    return backend_types


def compute_signatures_from_typeobjects(
    types_in, backend_type_formatter
) -> List[List[str]]:
    """Compute a list of lists (signatures) of strings (pythran types)

    """
    if isinstance(types_in, dict):
        types_in = types_in.values()

    types = []
    for type_ in types_in:
        if isinstance(type_, str):
            type_ = str2type(type_)
        types.append(type_)

    template_parameters = set()
    for type_ in types:
        if hasattr(type_, "get_template_parameters"):
            template_parameters.update(type_.get_template_parameters())

    if not template_parameters:
        str_types = []
        for type_ in types:
            if isinstance(type_, type):
                str_type = type_.__name__
            else:
                str_type = type_
            str_types.append(str_type)

        if "_empty" in str_types:
            raise ValueError(
                "At least one annotation type lacking in a signature.\n"
                f"types = {types}"
            )
        return (str_types,)

    if not all(param.values for param in template_parameters):
        raise ValueError(
            f"{template_parameters}, {[param.values for param in template_parameters]}"
        )

    values_template_parameters = {}
    for param in template_parameters:
        values_template_parameters[param.__name__] = param.values

    backend_types = []
    names = values_template_parameters.keys()
    for set_types in itertools.product(*values_template_parameters.values()):
        template_variables = dict(zip(names, set_types))

        backend_types.append(
            _format_types_as_backend_types(
                types, backend_type_formatter, **template_variables
            )
        )

    return backend_types


def _make_signature_from_template_variables(
    func, backend_type_formatter, _signature=None, as_list_str=False, **kwargs
):
    """Create signature for a function with values for the template types

    (This function should only be used in
    :func:`make_signatures_from_typehinted_func`)

    Parameters
    ----------

    func: a function

    kwargs : dict

        The template types and their value

    """
    if _signature is None:
        _signature = inspect.signature(func)

    types = [param.annotation for param in _signature.parameters.values()]

    backend_types = _format_types_as_backend_types(
        types, backend_type_formatter, **kwargs
    )

    # "multiply" the signatures to take into account the "or" syntax
    multi_pythran_types = [
        _ for _ in itertools.product(*[t.split(" or ") for t in backend_types])
    ]
    signatures = []
    for backend_types in multi_pythran_types:
        if as_list_str:
            signature = backend_types
        else:
            signature = f"{func.__name__}(" + ", ".join(backend_types) + ")"
        signatures.append(signature)

    return signatures


def make_signatures_from_typehinted_func(
    func, backend_type_formatter, as_list_str=False
):
    """Make the signatures from annotations if it is possible

    Useful when there are only "not templated" types.

    """
    annotations = func.__annotations__

    if not annotations:
        return tuple()

    for key, value in annotations.items():
        if isinstance(value, str):
            annotations[key] = str2type(value)

    types = annotations.values()

    template_parameters = []
    for type_ in types:
        if hasattr(type_, "get_template_parameters"):
            template_parameters.extend(type_.get_template_parameters())
    template_parameters = set(template_parameters)

    _signature = inspect.signature(func)

    if not template_parameters:
        signatures = _make_signature_from_template_variables(
            func,
            backend_type_formatter,
            _signature=_signature,
            as_list_str=as_list_str,
        )
        return signatures

    if not all(param.values for param in template_parameters):
        return tuple()

    values_template_parameters = {}
    for param in template_parameters:
        values_template_parameters[param.__name__] = param.values

    names = values_template_parameters.keys()
    signatures = []
    for set_types in itertools.product(*values_template_parameters.values()):
        template_variables = dict(zip(names, set_types))
        signatures.extend(
            _make_signature_from_template_variables(
                func,
                backend_type_formatter,
                _signature=_signature,
                as_list_str=as_list_str,
                **template_variables,
            )
        )

    return signatures
