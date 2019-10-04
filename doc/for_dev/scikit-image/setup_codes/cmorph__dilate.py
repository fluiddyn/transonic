import numpy as np
from future.cmorph import _dilate

rows = 1024
cols = 1024
srows = 64
scols = 64

image = np.random.randint(0, 255, rows * cols, dtype=np.uint8).reshape(
    (rows, cols)
)
selem = np.random.randint(0, 1, srows * scols, dtype=np.uint8).reshape(
    (srows, scols)
)
out = np.zeros((rows, cols), dtype=np.uint8)
shift_x = np.int8(2)
shift_y = np.int8(2)