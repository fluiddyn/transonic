import numpy as np


def is_valid_distance_matches_1ray(candidate, approved_matches_ray):
    _, ray_id = candidate
    if ray_id:
        other_closest_points = approved_matches_ray[ray_id]
        return len(other_closest_points) > 1
    return True


def kernel_make_approved_matches__min_distance_matches_1ray(candidates):
    approved_matches_ray: dict[np.int32, list[int]] = {}
    candidate = candidates[0]
    assert is_valid_distance_matches_1ray(candidate, approved_matches_ray)
    ray_id = candidate[1]
    approved_matches_ray.setdefault(ray_id, [])
    other_closest_points = approved_matches_ray[ray_id]
    other_closest_points.append(1)
    return approved_matches_ray


def __transonic__():
    return "0.7.3"
