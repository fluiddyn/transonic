from transonic import boost

@boost
class MyClass:

    a : int

    def __init__(self, a):
        self.a = a
    @boost
    def method(self, b : int):
        return self.a + b
    
    @boost
    def method2(self, b : int):
        return self.a + b
@boost
class MyClass2:

    a : int

    def __init__(self, a):
        self.a = a
    @boost
    def method(self, b : int):
        o : int
        o = 1
        return self.a + b + o

    @boost
    def method2(self, b : int):
        return self.a + b

    def method3(self, b : int):
        return self.a + b