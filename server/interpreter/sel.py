# -*- coding: utf-8 -*-

"""
SEL formats definations.
just migrate from ipmitool : ipmi_sel.h
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from ctypes import *

class standard_spec_sel_rec(LittleEndianStructure):
    """
    SEL record format
    """
    _fields_ = [('timestamp', c_uint32),
                ('gen_id', c_uint16),
                ('evm_rev', c_uint8),
                ('sensor_type', c_uint8),
                ('sensor_num', c_uint8),
                ('event_type', c_uint8, 7),
                ('event_dir', c_uint8, 1),
                ('event_data', c_uint8 * 3)]

class oem_ts_spec_sel_rec(LittleEndianStructure):
    """
    OEM timestamped
    """
    _fields_ = [('timestamp', c_uint32),
                ('manf_id', c_uint8 * 3),
                ('oem_defined', c_uint8 * 6)]

class oem_nots_spec_sel_rec(LittleEndianStructure):
    """
    OEM non-timestamped
    """
    _fields_ = [('oem_defined', c_uint8 * 13)]

class sel_type(Union):
    """
    SEL detail Union, include 3 types of SEL
    """
    _fields_ = [('standard_type', standard_spec_sel_rec),
                ('oem_ts_type', oem_ts_spec_sel_rec),
                ('oem_nots_type', oem_nots_spec_sel_rec)]

class sel_event_record(LittleEndianStructure):
    """
    SEL entry format struct
    """
    _fields_ = [('record_id', c_uint16),
                ('record_type', c_uint8),
                ('sel_type', sel_type)]
    _pack_ = 1

class sel_union(Union):
    """
    SEL data union, initialize with hex string
    """
    _fields_ = [('sel', sel_event_record),
                ('_data', c_uint8 * 16)]

    def __init__(self, data):
        super(sel_union, self).__init__()
        for i in xrange(16):
            self._data[i] = int(data[i*2:i*2+2], 16)

if __name__ == '__main__':
    # unit test
    sel = sel_union('010002c853245420000410726f02ffff')
    # 0100 02 c8532454 2000 04 10 72 6f 02ffff
    print '0x%x' % sel.sel.record_id
    print '0x%x' % sel.sel.record_type

    print '0x%x' % sel.sel.sel_type.standard_type.timestamp
    print '0x%x' % sel.sel.sel_type.standard_type.gen_id
    print '0x%x' % sel.sel.sel_type.standard_type.evm_rev
    print '0x%x' % sel.sel.sel_type.standard_type.sensor_type
    print '0x%x' % sel.sel.sel_type.standard_type.sensor_num
    print '0x%x' % sel.sel.sel_type.standard_type.event_type
    print '0x%x' % sel.sel.sel_type.standard_type.event_dir
    print '0x%x' % sel.sel.sel_type.standard_type.event_data[0]
    print '0x%x' % sel.sel.sel_type.standard_type.event_data[1]
    print '0x%x' % sel.sel.sel_type.standard_type.event_data[2]
