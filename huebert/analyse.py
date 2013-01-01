#!/usr/bin/python

import logging
import ctypes
import os

# get the directory this source is in
source_dir = os.path.dirname(__file__)

# load library
lib = ctypes.CDLL(os.path.join(source_dir, 'signal.so'))

def rms(data, signed, depth, rate, channels):

    logging.debug('rms: signed = %d, depth = %d, rate = %d, channels = %d' % 
                  (signed, depth, rate, channels))

    v = lib.rms(data, len(data), signed, depth, rate, channels)

    logging.debug('rms: %f' % v)

    return v

