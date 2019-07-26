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
        return self.a + b

    @boost
    def method2(self, b : int):
        return self.a + b

