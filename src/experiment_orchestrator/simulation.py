#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random # TODO this is for debugging ; to remove

from enum import StrEnum, auto
from pathlib import Path

from config.protocol_file_format import RESERVED_ORIGIN_VALUE, ProtocolTimepointValues

from runtime.logging import log


class SimulationStatus(StrEnum):
    INITIAL = auto()
    LOADING = auto()
    LOADED = auto()
    MODIFYING = auto()
    MODIFIED = auto()
    RUNNING = auto()
    APOPTOSIS = auto()
    FINISHED = auto()
    MITOSIS = auto()

class Simulation:

    def __init__(self, step, duration, input, simulation_mode, modifications=None, name= None, exchange=30):
        # Not sure if unpacking here is really wise, maybe keep working with a dictionnary?
        self.step_number = step
        self.duration = duration    # in seconds
        self.input = input
        self.simulation_mode = simulation_mode
        self.modifications = modifications or {}
        self.name = name
        self.exchange = exchange
        # State variables
        self.from_origin = self._from_origin()
        self.status = SimulationStatus.INITIAL

    def _from_origin(self):
        return all((self.input, "origin" in self.input, self.input["origin"] == RESERVED_ORIGIN_VALUE))

    def _log_status(self):
        log.debug("Step %d (%s) is %s.", self.step_number, self.name, self.status)
 
    def load_initial_conditions(self, protocol_name, output_path, cell_nb):
        self.status = SimulationStatus.LOADING

        # Simplify logic by setting default values to all input fields
        self.input.setdefault("name", protocol_name)
        self.input.setdefault("origin", self.step_number-1)
        self.input.setdefault("timepoint", ProtocolTimepointValues.LAST)

        # Don't reload previous step
        if not self.input or all(
                (self.input["name"] == protocol_name,
                 self.input["origin"] == self.step_number-1,
                 self.input["timepoint"] == ProtocolTimepointValues.LAST)):
            self.status = SimulationStatus.LOADED
            self._log_status()
            return
        input_file = output_path / f"{self.input['name']}_{self.input['origin']}_{cell_nb}"
        # Open file
        # Read time point
        # Loop with modification function to load data

        # WARNING: The design currently doesn't support loading anything else than species concentrations.
        # TODO: check for existence of parameter files to upload
        pass

    def load_modifications(self):
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
        return random.choice([SimulationStatus.APOPTOSIS, SimulationStatus.FINISHED, SimulationStatus.MITOSIS])

    def reset(self):
        # Revert here any changes made to the object
        self.status = SimulationStatus.INITIAL
        self._log_status()


