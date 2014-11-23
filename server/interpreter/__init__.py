# -*- coding: utf-8 -*-

"""
Interpreter for ipmitool's output.
To use this module, please ensure your ipmitool command is running with argument '-vv'
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

import itertools

from interpreter import sel
from interpreter import table
from interpreter import Default

def _description(out):
    """
    decode SEL description from output string.

    :param out: string from standard output
    :yeild:     description dictionary
    """

    desc = {}
    flag = False
    for line in out.splitlines():
        if 'SEL Record ID' in line:
            flag = True
            desc = {}

        if len(line) == 0:
            if flag:
                flag = False
                yield desc

        if flag:
            key, sep, value = line.partition(':')
            desc[key.strip()] = value.strip()

def _entry(err):
    """
    decode SEL raw entry from error string.

    :param err: string from standard error
    :yeild:     raw entry string
    """

    for line in err.splitlines():
        if 'SEL Entry' in line:
            yield line.split(':')[1].strip()

def _dispatch(desc, entry):
    """
    dispatch the SEL entry to an interpreter.

    :param desc:  dictionary for SEL description
    :param entry: raw entry for SEL description
    :returns:     (information, level) for given SEL entry
    """

    s = sel.sel_union(entry)

    interpreter_queue = table.DEFAULT_QUEUE
    if s.sel.record_type >= 0xc0:
        # OEM timestamped & non-timestamped
        interpreter_queue = table.OEM_RECORD_TABLE.get(s.sel.record_type,
                                                       table.DEFAULT_QUEUE)
    elif s.sel.record_type == 0x02:
        # system event record
        event_type = s.sel.sel_type.standard_type.event_type
        if event_type == 0x6f:
            # sensor-specific
            interpreter_queue = table.OEM_SENSOR_TABLE.get(s.sel.sel_type.standard_type.sensor_type,
                                                           table.DEFAULT_QUEUE)
        elif event_type >= 0x70 and event_type <= 0x7f:
            # OEM event
            interpreter_queue = table.OEM_EVENT_TABLE.get(event_type,
                                                          table.DEFAULT_QUEUE)

    result = None
    for interpreter in interpreter_queue:
        result = interpreter.interpret(desc, s)
        if result != None:
            break

    if result == None:
        for interpreter in table.DEFAULT_QUEUE:
            result = interpreter.interpret(desc, s)
            if result != None:
                break

    return result

def interpret(out, err):
    """
    interpret ipmitool's output

    :param out: string from standard output
    :param err: string from standard error
    :returns:   list of interpreted infomation
    """

    ans = []
    for desc, entry in itertools.izip(_description(out), _entry(err)):
        ans.append(_dispatch(desc, entry))

    return ans
