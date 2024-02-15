from transonic import boost, Transonic

# used for testing
ts = Transonic()


@boost
def compute():
    return 1
