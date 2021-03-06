#!/usr/bin/python

# hacked from
# decodebin.py - Audio autopluging example using 'decodebin' element
# Copyright (C) 2006 Jason Gerard DeRose <jderose@jasonderose.org>

# /usr/share/gst-python/0.10/examples/decodebin.py

# test with eg.
# ./gstreamer-test.py ~/music/Kylie\ Minogue/Spinning\ Around\ \(Disc\ 1\)/01\  Spinning\ Around.mp3

import sys
import logging
import random

import gobject
gobject.threads_init()

import pygst
pygst.require('0.10')
import gst

import analyse
import error

class Audio:
    def __init__(self, location, controller = None):
        # these are set in on_handoff() from the stream caps
        self.signed = None
        self.depth = None
        self.rate = None
        self.channels = None

        self.controller = controller

        self.last_v = 1

        # The pipeline
        self.pipeline = gst.Pipeline()

        # Create bus and connect several handlers
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)

        # Create elements
        self.src = gst.element_factory_make('filesrc')
        self.dec = gst.element_factory_make('decodebin')
        self.conv = gst.element_factory_make('audioconvert')
        self.rsmpl = gst.element_factory_make('audioresample')
        self.ident = gst.element_factory_make('identity')
        self.queue = gst.element_factory_make('queue')
        self.sink = gst.element_factory_make('alsasink')

        # Set 'location' property on filesrc
        self.src.set_property('location', location)

        self.ident.connect('handoff', self.on_handoff)

        # queue 1s of audio, allow any number of buffers and bytes
        self.queue.set_property('max-size-buffers', 0)
        self.queue.set_property('max-size-bytes', 0)
        self.queue.set_property('max-size-time', 1000000000)
        self.queue.connect('overrun', self.on_overrun)
        self.queue.connect('underrun', self.on_underrun)
        self.queue.connect('pushing', self.on_pushing)
        self.queue.connect('running', self.on_running)

        # Connect handler for 'new-decoded-pad' signal 
        self.dec.connect('new-decoded-pad', self.on_new_decoded_pad)

        # Add elements to pipeline
        self.pipeline.add(self.src, self.dec, self.conv, self.rsmpl, 
                          self.ident, self.queue, self.sink)

        # Link *some* elements 
        # This is completed in self.on_new_decoded_pad()
        self.src.link(self.dec)
        gst.element_link_many(self.conv, self.rsmpl, 
                              self.ident, self.queue, self.sink)
        
        # Reference used in self.on_new_decoded_pad()
        self.apad = self.conv.get_pad('sink')

        # The MainLoop
        self.mainloop = gobject.MainLoop()

    def play(self):
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.mainloop.run()

    def on_new_decoded_pad(self, element, pad, last):
        caps = pad.get_caps()
        name = caps[0].get_name()
        logging.debug('on_new_decoded_pad: %s' % name)
        if name == 'audio/x-raw-float' or name == 'audio/x-raw-int':
            if not self.apad.is_linked(): # Only link once
                pad.link(self.apad)

    def on_overrun(self, element):
        logging.debug('on_overrun')

    def on_underrun(self, element):
        logging.debug('on_underrun')

    def on_running(self, element):
        logging.debug('on_running')

    def on_pushing(self, element):
        logging.debug('on_pushing')

    def on_eos(self, bus, msg):
        logging.debug('on_eos')
        self.mainloop.quit()

    def on_error(self, bus, msg):
        error = msg.parse_error()
        print 'on_error:', error[1]
        self.mainloop.quit()

    def on_handoff(self, element, buf):
        logging.debug('on_handoff - %d bytes' % len(buf))
        #print 'buf =', buf
        #print 'dir(buf) =', dir(buf)

        if self.signed == None:
            # only ever one caps struct on our buffers
            struct = buf.get_caps().get_structure(0)

            # I think these are always set too, but catch just in case
            try:
                self.signed = struct["signed"]
                self.depth = struct["depth"]
                self.rate = struct["rate"]
                self.channels = struct["channels"]
            except:
                logging.debug('on_handoff: missing caps')

        raw = str(buf)

        v = analyse.rms(raw, self.signed, self.depth, self.rate, self.channels)
        v |= 1

        if self.controller:
            light = random.randint(1, 3)
            hue = random.randint(0, 65535)
            sat = 254

            if float(v) / self.last_v > 1.5:
                bri = 254
            elif float(v) / self.last_v < 0.5:
                bri = 0
            else:
                bri = 128
            self.last_v = v

            # bri = 254 * random.randint(0, 1)

            self.controller.set_light(light, 
                                      {"bri": bri, 
                                       "hue": hue, 
                                       "sat": sat, 
                                       "on": True, 
                                       "transitiontime": 3})

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    if len(sys.argv) == 2:
        Audio(sys.argv[1])
    else:
        print 'Usage: %s /path/to/media/file' % sys.argv[0]
