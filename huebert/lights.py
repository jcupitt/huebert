#!/usr/bin/python

# add the python-requests package to get this
import requests

import json
import time
import logging
import random

import error

class Controller:

    # limit updates to 20 per second -- we become unreliable beyond this
    max_updates = 20.0

    def __init__(self, app_name, app_key, hue_url):
        self.app_name = app_name
        self.app_key = app_key
        self.hue_url = hue_url

        self.init = False
        self.state = None
        self.last_time = time.time()
        self.n_change = 0

    def post(self, location = None, data = None):
        logging.debug('post: location = %s, data = %s' % (location, data))

        url = self.hue_url + '/api'
        if location:
            url += '/' + location

        post_data = json.dumps(data).encode('utf-8')

        reply = requests.post(url, post_data) 

        output = reply.json

        logging.debug('reply = %s' % output)

        return output

    def get(self, location = None):
        logging.debug('get: location = %s' % location)

        url = self.hue_url + '/api'
        if location:
            url += '/' + location

        reply = requests.get(url)

        output = reply.json

        logging.debug('reply = %s' % output)

        return output

    def put(self, location = None, data = None):
        logging.debug('put: location = %s, data = %s' % (location, data))

        url = self.hue_url + '/api'
        if location:
            url += '/' + location

        put_data = json.dumps(data).encode('utf-8')

        reply = requests.put(url, put_data) 

        output = reply.json

        logging.debug('reply = %s' % output)

        return output

    def set_light(self, lamp, state):
        # ignore if this is too soon
        new_time = time.time() 
        if new_time - self.last_time < 1.0 / self.max_updates:
            return
        self.last_time = new_time

        location = '/'.join([str(self.app_key), 'lights', 
                             str(lamp), 'state'])

        return self.put(location, state)

    def debugstate(self):
        logging.debug('state: %s' % json.dumps(self.state, 
                                               sort_keys=True,
                                               indent=4, 
                                               separators=(',', ':')))

    def json_iserror(self, reply):
            if len(reply) != 1:
                return  False
            keys = reply[0].keys()
            if len(keys) != 1:
                return  False
            if keys[0] != "error":
                return  False

            return  True

    def register(self):
        logging.debug('registering application ...')

        # attempt a get with our key to see if we are already registered
        self.state = self.get(str(self.app_key))
        if not self.json_iserror(self.state):
            self.debugstate()
            logging.debug('already registered')
            return

        app_register = { 'username': str(self.app_key), 
                         'devicetype': self.app_name 
                       }

        while True:
            reply = self.post(None, app_register)

            if not self.json_iserror(reply):
                break

            time.sleep(0.5)

        self.state = self.get('')
        self.debugstate()

        logging.debug('registered!')

        self.init = True

if __name__ == '__main__':
    #logging.basicConfig(level = logging.DEBUG)

    # "hue" is bound in /etc/hosts to the ip address of my hue controller
    controller = Controller('huebert', 0xdeadbeef, "http://hue")

    controller.register()

    while True:
        light = random.randint(1, 3)
        hue = random.randint(0, 65535)
        sat = 254
        bri = 254

        controller.set_light(light, {"bri": bri, "hue": hue, "sat": sat, 
                                 "on": True, "transitiontime": 0})
