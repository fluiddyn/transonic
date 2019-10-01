from setuptools import setup, find_packages
from runpy import run_path as run_path
from pathlib import Path

here = Path(__file__).parent.absolute()

d = run_path(here / "transonic/_version.py")
__version__ = d["__version__"]
__about__ = d["__about__"]

print(__about__)

setup(
    version=__version__,
    packages=find_packages(exclude=["doc", "tmp", "data_tests"]),
    entry_points={"console_scripts": ["transonic = transonic.run:run"]},
)
