
def mysum(arr):
    ret = arr.dtype.type(0)
    for i in range(arr.shape[0]):
        ret += arr[i]
    return ret