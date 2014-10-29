# -*- coding: utf-8 -*-

"""
This module include some useful functions.
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

import re

def is_valid_ip_address_v4(address):
    """
    validate if the input string is an IPV4 address using re.

    :param address: input string to be checked
    :returns:       boolean value
    """

    prog = re.compile(
        r'^((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.){3}(?:(2[0-4]\d)|(255[0-5])|([01]?\d\d?))$'
    )

    if prog.match(address) == None:
        return False
    else:
        return True
