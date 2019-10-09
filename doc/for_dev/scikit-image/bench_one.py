import argparse
from bench_util import bench_one

parser = argparse.ArgumentParser(description="Run one benchmark")

parser.add_argument("module", help="Module name")

args = parser.parse_args()

bench_one(args.module)
