# -*- coding: utf-8 -*-

"""
Abstract base class for interpreter
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

import abc

from interpreter import table

class Base(object):
    """
    Abstract Base class for all interpreter
    """

    __metaclass__ = abc.ABCMeta

    def _append_to_table(self, target_table, key):
        """
        append self to target table with key.

        :param target_table: target table
        :param key:          key
        """

        interpreter_queue = target_table.get(key, [])
        interpreter_queue.append(self)
        target_table[key] = interpreter_queue

    def _register_oem_record(self, record_type):
        """
        register self as a interpreter for OEM record.

        :param record_type: record_type between 0xC0 to 0xFF
        """

        if record_type >= 0xc0 and record_type <= 0xff:
            self._append_to_table(table.OEM_RECORD_TABLE, record_type)
        else:
            raise Exception('Invalid OEM record type')

    def _register_oem_event(self, event_type):
        """
        register self as a interpreter for OEM event.

        :param event_type: event_type between 0x70 to 0x7F
        """

        if event_type >= 0x70 and event_type <= 0x7f:
            self._append_to_table(table.OEM_EVENT_TABLE, event_type)
        else:
            raise Exception('Invalid OEM event type')

    def _register_oem_sensor(self, sensor_type):
        """
        register self as a interpreter for senser-specific type.

        :param sensor_type: sensor_type
        """

        self._append_to_table(table.OEM_SENSOR_TABLE, sensor_type)

    def _register_system_event(self):
        """
        register self as a default interpreter.
        """

        table.DEFAULT_QUEUE.append(self)

    @abc.abstractmethod
    def interpret(self, desc, sel):
        """
        abstract method for all interpreter.

        :param desc: description dictionary
        :param sel:  SEL data structure
        :return:     (id, type, datetime, level, desc, info)
        """
        pass
