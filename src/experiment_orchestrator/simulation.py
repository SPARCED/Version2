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

    def retrieve_initial_conditions(self):
        # Retrieve input data:
        # - needs output_path from WORKER
        # - reconstruct input file name from input (name, step)
        # - gather data depending on timepoint specification
        # - should be able to handle the step 0 origin
        pass

    def set_solver_initial_conditions(self):
        # Load input data:
        # - needs solver from WORKER
        # - use wrapper to load input data into solver

        # Apply modifications:
        # - needs solver from WORKER
        # - use wrapper to apply modifications data on solver
        pass

    def run(self):
        # Run simulation
        # - needs solver and cell_number + output_path from WORKER
        # - resolve output file name / path
        # - responsible for calls to simulation wrapper
        # - use a step by step method (like every 100 steps for example) to make regular saves
        
        # Handle the status
        # - determine simulation status (ALIVE, DEAD, DIVISION)
        # - return it to WORKER
        pass

