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
        # Set default values to all input fields & evaluate input type
        origin = {"name": protocol_name, "origin": RESERVED_ORIGIN_VALUE, "timepoint": ProtocolTimepointValues.FIRST }
        previous = {"name": protocol_name, "origin": self.infos.step-1, "timepoint": ProtocolTimepointValues.LAST }
        self._set_input_fields(origin, previous)
        self.is_from_origin = self._input_is_from(origin)
        self.is_from_previous = self._input_is_from(previous)
        # State variables
        self.status = SimulationStatus.INITIAL
        self._log_status()

    def _input_is_from(self, tested):
        return all(self.infos.input[k] == tested[k] for k in tested)

    def _log_status(self):
        log.debug("Step %d (%s) is %s.", self.infos.step, self.infos.name, self.status)

    def _set_input_fields(self, origin, previous):
        if self.infos.input is not None:
            for k, v in previous.items():
                self.infos.input.setdefault(k, v)
        else:
            for k, v in origin.items():
                self.infos.input.setdefault(k, v)

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

    def load_modifications(self, solver):
        for k, v in self.infos.modifications.items():
            log.debug(f"{k} changed to {v}")
            solver.modify(k, v)

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

