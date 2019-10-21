# Numba backend

This backend is currently minimalist: Transonic only creates Python files using
the decorator `numba.njit`.

- No proper ahead-of-time compilation is done even with the `boost` decorator.

- The types in annotations are not used for this backend.
