#!/usr/bin/python

import sys
import logging

# we can't use argparse, we need to work on OS X which is still 
# stuck on python 2.5
import optparse

import audio
import controller

music = '/home/john/music/'
track = music + 'Kylie Minogue/Spinning Around (Disc 1)/01 Spinning Around.mp3'
track = music + 'Parry Gripp/Fuzzy Fuzzy Cute Cute_ Volume 1/03 Cat Flushing A Toilet.m4a'

def main():
    global options
    global track

    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug", 
                    action = "store_true", dest = "verbose", default = False, 
                    help = "print debug messages")
    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level = logging.DEBUG)

    # "hue" is bound in /etc/hosts to the ip address of my hue controller
    cont = controller.Controller('huebert', 0xdeadbeef, "http://hue")
    cont.register()

    aud = audio.Audio(track, cont)

    aud.play()

if __name__ == '__main__':
    main()
