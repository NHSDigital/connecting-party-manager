def a(data, cache):
    return {"blah", "hi"}


def b(data, cache):
    return {"a's result": data[a]}


steps = [a, b]
