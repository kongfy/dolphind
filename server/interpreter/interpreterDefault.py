# -*- coding: utf-8 -*-

"""
Default interpreter
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

import datetime

from interpreter import Base

LEVEL_MAP = {
    0x20 : 'HW', # BMC
    0x01 : 'HW', # BIOS POST
    0x33 : 'HW', # BIOS SMI
    0xc0 : 'HW', # Hot Swap Controller Firmware
    0xc2 : 'HW',
    0x2c : 'HW', # Node Manager/ME Firmware
    0x41 : 'OS', # Microsoft OS
    0x21 : 'OS', # Linux Kernel Panic Event
}

class Default(Base.Base):
    """
    Default interpreter
    """

    def __init__(self):
        self._register_system_event()

    def _level(self, sel):
        """
        level for sel

        :param sel: SEL data structure
        :returns:   level
        """
        if sel.sel.record_type == 0x02:
            # system event record
            return LEVEL_MAP.get(sel.sel.sel_type.standard_type.gen_id,
                                 'OTHER')
        return 'OTHER'

    def interpret(self, desc, sel):
        """
        Default interpreter method

        :param desc: description dictionary
        :param sel:  SEL data structure
        :returns:    (id, type, datetime, level, severity, desc, info)
        """

        sel_datetime = desc.get('Timestamp', None)

        return (sel.sel.record_id,
                sel.sel.record_type,
                datetime.datetime.strptime(sel_datetime, '%m/%d/%Y %H:%M:%S'),
                self._level(sel),
                'ERROR',
                desc.get('Description', 'Unknown SEL'),
                desc)

INST = Default()
