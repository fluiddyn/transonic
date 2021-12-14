# Old performance regression between pythran 0.9.5 and 0.9.6

To install compatible versions of Pythran, Gast and Beniget (and Transonic, but
which is used only for its timeit function, I used
[pypi-timemachine](https://github.com/astrofrog/pypi-timemachine) in a clean
virtual environment.

```
pip install pythran transonic --index-url http://localhost:58888
```

The regression is between

```
pypi-timemachine 2020-01-03  # pythran 0.9.5
```

and

```
pypi-timemachine 2020-08-02  # pythran 0.9.6
```

The former (pythran 0.9.5) gives:

```
pythran mod_pythran.py -DUSE_XSIMD -Ofast -march=native
python bench.py
Transonic 0.4.2
Pythran 0.9.5
[...]
fxfy                             : 1.000 * norm
norm = 2.05e-04 s
fxfy_pythran                     : 0.232 * norm
fxfy_loops_pythran               : 0.803 * norm
```

and the later (pythran 0.9.6) gives

```
pythran mod_pythran.py -DUSE_XSIMD -Ofast -march=native
python bench.py
Transonic 0.4.3
Pythran 0.9.6
[...]
fxfy                             :     1 * norm
norm = 0.000208 s
fxfy_pythran                     : 0.883 * norm
fxfy_loops_pythran               : 0.798 * norm
```
