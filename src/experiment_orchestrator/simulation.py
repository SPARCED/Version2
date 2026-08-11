#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.protocol_file_format import VALID_INPUT_KEYS, VALID_MODIFICATIONS_KEYS, VALID_SIMULATION_MODE_VALUES, VALID_TIMEPOINT_VALUES


class Simulation:

    def __init__(self, step, duration, input, simulation_mode, modifications=None, name= None, exchange=30):
        self.step_number = step
        self.duration = duration    # in seconds
        self.input = input
        self.simulation_mode = simulation_mode
        self.modifications = modifications or {}
        self.name = name
        self.exchange = exchange

        self._validate()

    def _validate(self):
        self._validate_general_parameters()
        self._validate_input()
        self._validate_modifications()
        self._validate_simulation_mode()

    def _validate_general_parameters(self):
        # Step number
        if not isinstance(self.step_number, int):
            raise TypeError("Step must be an integer")
        elif self.step_number < 0:
            raise ValueError("Step must be a positive integer")
        elif self.step_number == 0:
            raise ValueError("Step 0 is reserved for original input data")

        # Duration
        if not isinstance(self.duration, int):
            raise TypeError("Duration must be an integer")
        elif self.duration <= 0:
            raise ValueError("Duration must be a positive integer")

    def _validate_input(self):
        unknown = set(self.input) - VALID_INPUT_KEYS
        if unknown:
            raise ValueError(f"Unknown input data key: {unknown}")
        if "timepoint" in self.input and not self.input["timepoint"] in VALID_TIMEPOINT_VALUES:
            raise ValueError(f"Unknown input timepoint value: {self.input['timepoint']}")

    def _validate_modifications(self):
        unknown = set(self.modifications) - VALID_MODIFICATIONS_KEYS
        if unknown:
            raise ValueError(f"Unknown modifications key: {unknown}")

    def _validate_simulation_mode(self):
        if self.simulation_mode not in VALID_SIMULATION_MODE_VALUES:
            raise ValueError(f"Unknown simulation mode: {self.simulation_mode}")

        # Load simulation data
        # Apply modifications (order is extremely important)
        # Set simulation mode, time, step (start /step / stop)
        # Storage path could be usefull

    def run(self):
        pass
        # Outputs species over time
        # Sends back status (cell alive, dead, division)

