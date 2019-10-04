import numpy as np
from future._greyreconstruct import reconstruction_loop

from skimage.filters._rank_order import rank_order

y, x = np.mgrid[:20:0.5, :20:0.5]
bumps = np.sin(x) + np.sin(y)
h = 0.3
seed = bumps - h
mask = bumps

assert tuple(seed.shape) == tuple(mask.shape)

selem = np.ones([3] * seed.ndim, dtype=bool)
offset = np.array([d // 2 for d in selem.shape])

# Cross out the center of the selem
selem[tuple(slice(d, d + 1) for d in offset)] = False

# Make padding for edges of reconstructed image so we can ignore boundaries
dims = np.zeros(seed.ndim + 1, dtype=int)
dims[1:] = np.array(seed.shape) + (np.array(selem.shape) - 1)
dims[0] = 2
inside_slices = tuple(slice(o, o + s) for o, s in zip(offset, seed.shape))
# Set padded region to minimum image intensity and mask along first axis so
# we can interleave image and mask pixels when sorting.
pad_value = np.min(seed)

images = np.full(dims, pad_value, dtype="float64")
images[(0, *inside_slices)] = seed
images[(1, *inside_slices)] = mask

# Create a list of strides across the array to get the neighbors within
# a flattened array
value_stride = np.array(images.strides[1:]) // images.dtype.itemsize
image_stride = np.int64(images.strides[0] // images.dtype.itemsize)
selem_mgrid = np.mgrid[[slice(-o, d - o) for d, o in zip(selem.shape, offset)]]
selem_offsets = selem_mgrid[:, selem].transpose()
nb_strides = np.array(
    [np.sum(value_stride * selem_offset) for selem_offset in selem_offsets],
    np.int32,
)

images = images.flatten()

# Erosion goes smallest to largest; dilation goes largest to smallest.
index_sorted = np.argsort(images).astype(np.int32)
index_sorted = index_sorted[::-1]

# Make a linked list of pixels sorted by value. -1 is the list terminator.
prev = np.full(len(images), -1, np.int32)
next_ = np.full(len(images), -1, np.int32)
prev[index_sorted[1:]] = index_sorted[:-1]
next_[index_sorted[:-1]] = index_sorted[1:]

# Cython inner-loop compares the rank of pixel values.
value_rank, value_map = rank_order(images)

start = index_sorted[0]
ranks = np.array(value_rank)
strides = nb_strides
current_idx = np.int64(start)
