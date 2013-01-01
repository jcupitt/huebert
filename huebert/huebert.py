#!/usr/bin/python

import sys
import logging

# we can't use argparse, we need to work on OS X which is still 
# stuck on python 2.5
import optparse

import audio
import controller

def main():
    global options

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

    aud = audio.Audio('/home/john/music/Kylie Minogue/Spinning Around (Disc 1)/01 Spinning Around.mp3', cont)
    # aud = audio.Audio('/home/john/music/Parry Gripp/Fuzzy Fuzzy Cute Cute_ Volume 1/01 Fuzzy Fuzzy Cute Cute.m4a', cont)

    aud.play()

if __name__ == '__main__':
    main()
