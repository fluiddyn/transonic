import numpy as np

from transonic import boost


def is_valid_distance_matches_1ray(candidate, approved_matches_ray):
    _, ray_id = candidate
    if ray_id:
        other_closest_points = approved_matches_ray[ray_id]
        return len(other_closest_points) > 1
    return True


@boost
def kernel_make_approved_matches__min_distance_matches_1ray(
    candidates: "(int32, int32) list",
):
    approved_matches_ray: dict[np.int32, list[int]] = {}
    candidate = candidates[0]
    assert is_valid_distance_matches_1ray(candidate, approved_matches_ray)
    ray_id = candidate[1]
    approved_matches_ray.setdefault(ray_id, [])
    other_closest_points = approved_matches_ray[ray_id]
    other_closest_points.append(1)
    return approved_matches_ray
