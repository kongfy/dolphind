# -*- coding: utf-8 -*-

"""
dolphind base exception module
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]


class DException(Exception):
    """
    Base Dolphind Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """

    message = "An unknown exception occurred."
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.message % kwargs
            except Exception:
                message = self.message

        super(DException, self).__init__(message)

    def __str__(self):
        return 'Error %s : %s' % (self.code, self.message)

class InvalidIPAddr(DException):
    """
    Raise when IP address is not valid.
    """

    message = "Invalid IPv4 address."
    code = 400

class IPMIToolError(DException):
    """
    Raise when subprocess exit with code != 0
    """

    message = "Runtime error."
    code = 401

class RequestError(DException):
    """
    Raise when failed to query or validate request detail.
    """

    message = "illegal request"
    code = 402

class HostsError(DException):
    """
    Raise when failed to query hosts
    """

    message = "failed to get hosts"
    code = 403

class HostsNotFoundError(DException):
    """
    Raise when can not found any associated hosts
    """

    message = "hosts not found"
    code = 404

class IllegalHostError(DException):
    """
    Raise when host info is not qualified
    """

    message = "illegal host"
    code = 404

class DBUpdateError(DException):
    """
    Raise when filed to update database somewhere
    """

    message = "DB error"
    code = 405
