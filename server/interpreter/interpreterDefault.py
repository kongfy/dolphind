# -*- coding: utf-8 -*-

"""
Default interpreter
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

import datetime

from interpreter import Base

class Default(Base.Base):
    """
    Default interpreter
    """

    def __init__(self):
        self._register_system_event()

    def interpret(self, desc, sel):
        """
        Default interpreter method

        :param desc: description dictionary
        :param sel:  SEL data structure
        :return:     (id, type, datetime, level, desc, info)
        """

        sel_datetime = desc.get('Timestamp',
                                datetime.datetime.fromtimestamp(0))

        return (sel.sel.record_id,
                sel.sel.record_type,
                datetime.datetime.strptime(sel_datetime, '%m/%d/%Y %H:%M:%S'),
                'ERROR',
                desc.get('Description', 'Unknown SEL'),
                desc)

INST = Default()
