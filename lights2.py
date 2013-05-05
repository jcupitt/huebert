#!/usr/bin/python

# track a set of real lights, a set of target light settings, and a set of
# changes we want to make to the lights over time

# at each time interval, work out what state the lights should be in, then 
# perform the light change (we are only allowed one) that will bring the 
# real lights closest to the target

import time
import logging

import error

# Lights have three independent channels
# map these to HSB or RGB in output

class Light:

    def __init__(self):
        # current state
        self.current = [0, 0, 0]

        # currently transitioning to this state
        self.target = [0, 0, 0]

        # lights change by delta every tick for n_ticks
        # n_ticks counts down
        self.n_ticks = [0, 0, 0]
        self.delta = [0, 0, 0]

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
        for i in range(0, len(self.current)):
            s += (self.current[i] - other.current[i]) ** 2
        return s

    # issue a command on a light: try to change it to better match another

    def correct(self, other):
        self.current = other.current
        self.target = other.target
        self.n_ticks = other.n_ticks
        self.delta = other.delta

        self.controller.set_light(

        controller.set_light(light, {"bri": bri, "hue": hue, "sat": sat, 
                                 "on": True, "transitiontime": 0})

    # this needs to be called once for every 0.1s interval that passes
    def tick(self):
        for i in range(0, len(self.current)):
            if self.n_ticks[i] > 0:
                self.current[i] += self.delta[i]
                self.n_ticks[i] -= 1

            # at the end of transition, lock the light to the target to
            # make sure we don't accumulate rounding errors
            self.n_ticks == 0:
                self.hue = self.target_hue
                self.sat = self.target_sat
                self.bri = self.target_bri

class Command:

    # at time t, set channel i of light n 
    # time is in Gst units
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
        for i in range(0, self.n_lights):
            self.physical.append = Light()

        # the state requested by the queue of light change commands we process
        self.ideal = []
        for i in range(0, self.n_lights):
            self.ideal.append = Light()

        # the queue of light change commands we process
        self.queue = []

        # the current time our simulation is at 
        self.simulation_time = 0

    def command(self, t, n, i, value, transition):
        self.queue.append(Command(t, n, i, value, transition))

    # move the world forward by one 0.1s tick
    def cycle(self):
        self.simulation_time += 0.1

        # apply any commands which have become due
        while self.queue[0].time < self.simulation_time:
            c = self.queue[0]
            del self.queue[0]

            self.ideal[c.n].set_channel(c.i, c.value, c.transition)

        # update ideal and physical bulbs
        for i in range(0, self.n_lights):
            self.physical[i].tick()
            self.ideal[i].tick()

    # update for a new time point
    def update(self, time):
        # resort our queue of light-change commands by time
        queue.sort(key = lambda x: x.time)

        # round time down to the previous 0.1s boundary, ie. the most recent
        # tick point we can simulate to
        time = int(time * 10) / 10.0

        # run the simulation forward 0.1s at a time until we catch up
        while self.simulation_time < time:
            self.cycle()

            # find the two lights with the highest error
            worst = [self.physical[i].error(self.target[i]) 
                     for i in range(0, self.n_lights)]
            worst.sort(reverse = True)

            correct(worst[0])
            correct(worst[1])

