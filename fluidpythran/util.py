"""Internal utilities
=====================

Internal API
------------

.. autofunction:: get_module_name

.. autofunction:: modification_date

.. autofunction:: has_to_build

.. autofunction:: get_source_without_decorator

"""

import os
import inspect
from datetime import datetime
import re
from pathlib import Path

from typing import Callable


def get_module_name(frame):
    """Get the full module name"""
    module = inspect.getmodule(frame[0])
    if module is not None:
        module_name = module.__name__
        if module_name in ("__main__", "<run_path>"):
            module_name = inspect.getmodulename(frame.filename)
    else:
        module_name = inspect.getmodulename(frame.filename)
    return module_name


def modification_date(filename):
    """Get the modification date of a file"""
    return datetime.fromtimestamp(os.path.getmtime(filename))


def has_to_build(output_file: Path, input_file: Path):
    """Check if a file has to be (re)built"""
    output_file = Path(output_file)
    if not output_file.exists():
        return True
    mod_date_output = modification_date(output_file)
    if mod_date_output < modification_date(input_file):
        return True
    return False


def get_source_without_decorator(func: Callable):
    """Get the source of a function without its decorator"""
    src = inspect.getsource(func)
    return re.sub(r"@.*?\sdef\s", "def ", src)
