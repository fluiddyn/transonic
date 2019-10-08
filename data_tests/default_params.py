from transonic import boost, Optional


@boost
def func(a: int = 1, b: Optional[str] = None, c: float = 1.0):
    print(b)
    return a + c
