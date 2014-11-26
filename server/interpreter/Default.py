# -*- coding: utf-8 -*-

"""
Default interpreter
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from interpreter import Base

class Default(Base.Base):
    """
    Default interpreter
    """

    def __init__(self):
        self.register_system_event()

    def interpret(self, desc, sel):
        """
        Default interpreter method

        :param desc: description dictionary
        :param sel:  SEL data structure
        :return:     (id, type, level, desc, info)
        """

        return (sel.sel.record_id,
                sel.sel.record_type,
                desc.get('Timestamp', None),
                'ERROR',
                desc.get('Description', 'Unknown SEL'),
                desc)

INST = Default()
