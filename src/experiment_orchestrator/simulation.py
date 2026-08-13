#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Simulation:

    def __init__(self, step, duration, input, simulation_mode, modifications=None, name= None, exchange=30):
        self.step_number = step
        self.duration = duration    # in seconds
        self.input = input
        self.simulation_mode = simulation_mode
        self.modifications = modifications or {}
        self.name = name
        self.exchange = exchange

        # Load simulation data
        # Apply modifications (order is extremely important)
        # Set simulation mode, time, step (start /step / stop)
        # Storage path could be usefull

    def run(self):
        pass
        # Outputs species over time
        # Sends back status (cell alive, dead, division)

