from transonic import boost


@boost
class Myclass:
    attr: int
    attr2: int

    def __init__(self):
        self.attr = 1
        self.attr2 = 2

    @boost
    def func(self, arg: int):
        if self.func(arg - 1) < 1:
            return 1
        else:
            a = self.func(arg - 1) * self.func(arg - 1)
            return a + self.attr * self.attr2 * arg + self.func(arg - 1)
