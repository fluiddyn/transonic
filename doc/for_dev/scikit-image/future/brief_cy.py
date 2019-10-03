from transonic import boost

Ai2 = "int[:,:]"


@boost
def _brief_loop(
    image: "float64[:,:]",
    descriptors: "uint8[:,:]",
    keypoints: "intp[:,:]",
    pos0: Ai2,
    pos1: Ai2,
):
    for k in range(len(keypoints)):
        kr, kc = keypoints[k]
        for p in range(len(pos0)):
            pr0, pc0 = pos0[p]
            pr1, pc1 = pos1[p]
            descriptors[k, p] = (
                image[kr + pr0, kc + pc0] < image[kr + pr1, kc + pc1]
            )
