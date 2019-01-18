from transonic import boost, jit


@boost
class OtherClass:
    """Note that there is no type annotations at all!

    The Pythran signature is created at run time with the types of the
    attributes and the arguments.

    """

    def __init__(self, arg):
        self.attr0 = self.attr1 = 2 * arg

    @jit
    def calcul(self, a, b):
        return a * self.attr0 + b * self.attr1
