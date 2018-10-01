
from setuptools import setup, find_packages
from runpy import run_path

f"In >=2018, you should use a Python supporting f-strings!"

d = run_path("fluidpythran/_version.py")
__version__ = d["__version__"]
__about__ = d["__about__"]

print(__about__)


setup(version=__version__, packages=find_packages(exclude=["doc"]))
