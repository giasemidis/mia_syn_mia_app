# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 16:58:28 2018

@author: Georgios
"""

import os.path
import sys


def valid_file(func):
    """Checks the validity of the input file of read-data fuction. If files
    does not exist, it exists.
    """

    def wrapper(filename, *args, **kwargs):
        if os.path.isfile(filename):
            a = func(filename, *args, **kwargs)
            return a
        else:
            sys.exit('File %s not found' % filename)
            return
    return wrapper


def valid_folder(func):
    """Checks the validity of the output directory of a write-data function. If
    directory does not exist, it exists.
    """

    def wrapper(filepath, *args, **kwargs):
        dirname = os.path.dirname(filepath)
        dirname = dirname if dirname != '' else '.'
        if os.path.isdir(dirname):
            a = func(filepath, *args, **kwargs)
            return a
        else:
            sys.exit('Directory %s not found' % filepath)
            return
    return wrapper
