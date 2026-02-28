
import sys

class Error(Exception):
    pass

def open(f, mode=None):
    raise Error("aifc is not supported on this platform")

def _read_float(f):
    raise Error("aifc is not supported")

def _write_float(f, x):
    raise Error("aifc is not supported")
