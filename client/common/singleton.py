# -*- coding: utf-8 -*-

"""
Maybe the most useful Design Pattern : Singleton
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]


def singleton(cls):
    """
    Singleton pattern decorator. I's not thread safe, use it carefully.
    Warning: this is not a good way to implement singleton in Python
    You may just want to use python module instead of this.
    """

    instances = {}
    def _singleton(*args, **kwargs):
        """
        using class var 'instances' to implement Singleton.
        """
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
