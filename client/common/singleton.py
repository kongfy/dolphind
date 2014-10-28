def singleton(cls):
    instances = {}
    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return _singleton

if __name__ == '__main__':
    @singleton
    class SingleTest(object):
        def __init__(self, s): self.s = s
        def __str__(self): return self.s

    s1 = SingleTest('s1')
    s2 = SingleTest('s2')
    print id(s1), s1
    print id(s2), s2
