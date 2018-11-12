"""Internal utilities
=====================


"""

import os
import inspect
from datetime import datetime
import re


def get_module_name(frame):
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
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def has_to_build(output_file, input_file):
    """Check if a file has to be (re)built"""
    if not output_file.exists():
        return True
    mod_date_output = modification_date(output_file)
    if mod_date_output < modification_date(input_file):
        return True
    return False


def get_source_without_decorator(func):
    src = inspect.getsource(func)
    return re.sub(r"@.*?\sdef\s", "def ", src)
