# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 11:42:24 2018

@author: Georgios
"""

from dateutil import tz


def convert_timezone(time, from_tz='UTC', to_tz='Europe/Athens'):
    '''
    Convert 'time' from timezone 'from_tz' to timezone 'to_tz'
    '''
    from_zone = tz.gettz(from_tz)
    to_zone = tz.gettz(to_tz)
    time = time.replace(tzinfo=from_zone)
    new_time = time.astimezone(to_zone)

    return new_time
