from bench_util import bench_one, statements

for mod_name, func_name in statements.keys():
    bench_one(mod_name)
