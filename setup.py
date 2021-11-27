from setuptools import setup
from runpy import run_path as run_path
from pathlib import Path

here = Path(__file__).parent.absolute()

d = run_path(str(here / "transonic/_version.py"))
__version__ = d["__version__"]
__about__ = d["__about__"]

print(__about__)

setup(version=__version__)
