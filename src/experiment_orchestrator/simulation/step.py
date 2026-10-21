#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random # TODO this is for debugging ; to remove

from enum import StrEnum, auto
from pathlib import Path
from types import SimpleNamespace

from config.protocol_file_format import DefaultStepValues, RESERVED_ORIGIN_VALUE, ProtocolTimepointValues

from runtime.logging import log


class SimulationStatus(StrEnum):
    INITIAL = auto()
    LOADED = auto()
    MODIFIED = auto()
    RUNNING = auto()
    APOPTOSIS = auto()
    FINISHED = auto()
    MITOSIS = auto()

class SimulationStep:

    def __init__(self, details, protocol_name, generation):
        self.infos = SimpleNamespace(**(DefaultStepValues | details))
        self.generation = generation
        # Set default values to all input fields -- TODO: refactor in a function
        self.infos.input.setdefault("name", protocol_name)
        if self.infos.step is not None:
            self.infos.input.setdefault("origin", self.infos.step-1)
            self.infos.input.setdefault("timepoint", ProtocolTimepointValues.LAST)
        else:
            self.infos.input.setdefault("origin", RESERVED_ORIGIN_VALUE)
            self.infos.input.setdefault("timepoint", ProtocolTimepointValues.FIRST)
        # State variables
        self.status = SimulationStatus.INITIAL
        self._log_status()

    def _log_status(self):
        log.debug("Step %d (%s) is %s.", self.infos.step, self.infos.name, self.status)
 
    def load_initial_conditions(self, protocol_name, output_path, cell_nb):
        # Don't reload previous step
        if self.infos.step is not None and all(
                (self.infos.input["name"] == protocol_name,
                 self.infos.input["origin"] == self.infos.step - 1,
                 self.infos.input["timepoint"] == ProtocolTimepointValues.LAST)):
                    pass
        
        input_file = output_path / f"{self.infos.input['name']}_{self.infos.input['origin']}_{cell_nb}"
        # Open file
        # Read time point
        # Loop with modification function to load data

        # WARNING: The design currently doesn't support loading anything else than species concentrations.
        # TODO: check for existence of parameter files to upload
        
        self.status = SimulationStatus.LOADED
        self._log_status()

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
        if self.generation > 2:
            return SimulationStatus.APOPTOSIS
        return random.choice([SimulationStatus.APOPTOSIS, SimulationStatus.FINISHED, SimulationStatus.MITOSIS])

    def reset(self):
        # Revert here any changes made to the object
        self.status = SimulationStatus.INITIAL
        self._log_status()

