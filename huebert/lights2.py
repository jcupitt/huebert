#!/usr/bin/python

# track a set of real lights, a set of target light settings, and a set of
# changes we want to make to the lights over time

# at each time interval, work out what state the lights should be in, then 
# perform the light change (we are only allowed one) that will bring the 
# real lights closest to the target

import time
import logging
import random

import error

# number of channels per light ... RGB or HSB
channels = 3

# an array of channels with each element set to a value
def carray(x):
    return list((x,) * channels)

# Lights have three independent channels
# map these to HSB or RGB in output

class Light:
    def __init__(self, light):
        # the id of this light
        self.light = light

        # current state
        self.current = carray(0)

        # currently transitioning to this state
        self.target = carray(0)

        # lights change by delta every tick for n_ticks
        # n_ticks counts down
        self.n_ticks = carray(0)
        self.delta = carray(0)

    # interpolate linearly, no idea if the real lights do this

    # a transition time of 1 means that the lights change in one intermediate
    # step

    def set_channel(self, i, value, transition):
        if transition < 0:
            raise error.Error("Light setting out of range")

        self.target[i] = value
        self.n_ticks[i] = transition + 1
        self.delta[i] = (value - self.current[i]) / self.n_ticks[i]

    # calculate an error metric for a pair of lights

    # use square of difference, so we put more emphasis on brighter differences

    def error(self, other):
        s = 0

        for i in range(channels):
            s += (self.current[i] - other.current[i]) ** 2

        return s

    # correct a light: try to change self to match other

    # return the [[R, G, B], n_ticks] transition we've performed

    def correct(self, other):
        # we can only set one transition time, though we will set all three 
        # channels ... we have to set the nearest time in other as our target
        ticks = min(other.n_ticks)
        self.n_ticks = carray(ticks)

        # what colour will other be then
        self.target = [other.current[i] + ticks * other.delta[i] 
                       for i in range(channels)]

        if ticks > 0:
            self.delta = [(self.target[i] - self.current[i]) / ticks
                          for i in range(channels)]
        else:
            self.delta = carray(0)

        return [self.target, ticks]

    # run one cycle of the simulation

    # this needs to be called once for every 0.1s interval that passes
    def tick(self):
        for i in range(0, len(self.current)):
            if self.n_ticks[i] > 0:
                self.current[i] += self.delta[i]
                self.n_ticks[i] -= 1

            # at the end of transition, lock the light to the target to
            # make sure we don't accumulate rounding errors
            if self.n_ticks == 0:
                self.hue = self.target_hue
                self.sat = self.target_sat
                self.bri = self.target_bri

class Command:

    # at time t, set channel i of light n to value, transitioning over time
    # transition

    # time is in Gst units, transition is in 0.1s ticks

    def __init__(self, t, n, i, value, transition):
        self.time = t
        self.n = n
        self.i = i
        self.value = value
        self.transition = transition

class Lights:

    def __init__(self, n_lights, controller):
        self.n_lights = n_lights
        self.controller = controller

        # the current state of the physical lights, as far as we know
        self.physical = []
        for i in range(self.n_lights):
            self.physical.append(Light(i))

        # the state requested by the queue of light change commands we process
        self.ideal = []
        for i in range(self.n_lights):
            self.ideal.append(Light(i))

        # the queue of light change commands we process
        self.queue = []

        # the current time our simulation is at 
        self.simulation_time = 0

    def command(self, t, n, i, value, transition):
        logging.debug('lights.command: t = %f' % t)
        logging.debug('\tn = %d, i = %d, value = %d, transition = %d' % 
                      (n, i, value, transition))
        self.queue.append(Command(t, n, i, value, transition))

    # move the world forward by one 0.1s tick
    def cycle(self):
        self.simulation_time += 0.1

        # apply any commands which have become due
        while len(self.queue) > 0 and self.queue[0].time < self.simulation_time:
            c = self.queue[0]
            del self.queue[0]

            self.ideal[c.n].set_channel(c.i, c.value, c.transition)

        # update ideal and physical bulbs
        for i in range(0, self.n_lights):
            self.physical[i].tick()
            self.ideal[i].tick()

    # update for a new time point
    def update(self, time):
        logging.debug('lights.update: time = %f' % time) 
        logging.debug('lights.update: simulation_time = %f' % self.simulation_time) 
        logging.debug('lights.update: queue of %d commands' % len(self.queue))

        # resort our queue of light-change commands by time
        self.queue.sort(key = lambda x: x.time)

        # run the simulation forward 0.1s at a time until we catch up
        while self.simulation_time < time:
            self.cycle()

            # find the two lights with the highest error
            worst = [(i, self.physical[i].error(self.ideal[i]))
                     for i in range(0, self.n_lights)]
            worst.sort(key = lambda (i, error): error, reverse = True)

            for i in range(2):
                (light, error) = worst[i]
                physical = self.physical[light]
                ideal = self.ideal[light]
                [[R, G, B], n_ticks] = physical.correct(ideal)

                self.controller.set_light(light, 
                                          {"bri": R, "hue": G, "sat": B,
                                           "on": True, 
                                           "transitiontime": n_ticks})

class TestController:
    def set_light(self, light, command):
        print 'TestController: light %d' % light
        print '\t%s' % command

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    controller = TestController()
    lights = Lights(3, controller)

    world_time = 0
    while True:
        # at time t, set channel i of light n to value, transitioning over time
        # transition

        t = world_time + random.randint(1, 30) / 10
        i = random.randint(0, 2)
        n = random.randint(0, 2)
        value = random.randint(1, 255)
        transition = random.randint(1, 50)

        lights.command(t, n, i, value, transition)

        world_time += 0.1
        lights.update(world_time)

        time.sleep(0.2)
