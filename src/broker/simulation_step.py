#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import random   # TODO: remove ; this is for debugging purpose

from config.protocol_file_format import DefaultStepValues, RESERVED_ORIGIN_VALUE, ProtocolTimepointValues

from broker.runtime.logging import log

from broker.simulation_status import SimulationStatus

from solvers._abstract_solver import AbstractSolver


class SimulationStep:

    def __init__(self, details, protocol_name, generation=0):
        self.details = SimpleNamespace(**(DefaultStepValues | details))
        self.generation = generation
        self.protocol_name = protocol_name
        # Set default values to all input fields & evaluate input type
        origin = {"name": protocol_name, "origin": RESERVED_ORIGIN_VALUE, "timepoint": ProtocolTimepointValues.FIRST }
        previous = {"name": protocol_name, "origin": self.details.step-1, "timepoint": ProtocolTimepointValues.LAST }
        self._set_input_fields(origin, previous)
        self.is_from_origin = self._input_is_from(origin)
        self.is_from_previous = self._input_is_from(previous)
        # State variables
        self.status = SimulationStatus.INITIAL
        self._log_status()

    def _input_is_from(self, tested):
        return all(self.details.input[k] == tested[k] for k in tested)

    def _log_status(self):
        log.debug(f"Step {self.details.step} ({self.details.name}) is {self.status}.")

    def _set_input_fields(self, origin, previous):
        if not self.details.input:
            for k, v in origin.items():
                self.details.input.setdefault(k, v)
        else:
            for k, v in previous.items():
                self.details.input.setdefault(k, v)

    """
    def load_initial_conditions(self, output_path, cell_nb):
        # Don't reload previous step
        if self.infos.step is not None and all(
                (self.infos.input["name"] == self.protocol_name,
                 self.infos.input["origin"] == self.infos.step - 1,
                 self.infos.input["timepoint"] == ProtocolTimepointValues.LAST)):
                    pass
        
        input_file = output_path / f"{self.infos.input['name']}_step_{self.infos.input['origin']}_cell_{cell_nb}"
        # Open file
        # Read time point
        # Loop with modification function to load data

        # WARNING: The design currently doesn't support loading anything else than species concentrations.
        # TODO: check for existence of parameter files to upload
        
        self.status = SimulationStatus.LOADED
        self._log_status()
    """

    def apply_modifications(self, solver: AbstractSolver) -> None:
        for k, v in self.details.modifications.items():
            try:
                solver.modify(k, v)
            except ValueError as e:
                log.error(e)    # Termination is upon the user

        self.status = SimulationStatus.MODIFIED
        self._log_status()

    def reset(self):
        # Revert here any changes made to the object
        self.status = SimulationStatus.INITIAL
        self._log_status()

    def run(self, cell_id: int, solver: AbstractSolver, output_path: str | Path) -> SimulationStatus:
        self.status = SimulationStatus.RUNNING
        self._log_status()

        # Reconstruct output file path to store results
        results_name = f"{self.protocol_name}_step_{self.details.step}_cell_{cell_id}.tsv"
        results_path = output_path / results_name

        # Run a simulation
        results = solver.simulate(0, self.details.duration, self.details.exchange)
        
        # Save results
        results.to_csv(results_path, sep="\t", index=True)
        # TODO: perform regular saves, for example every 100 steps

        # Detect status
        self.status = SimulationStatus.FINISHED # random.choice([SimulationStatus.APOPTOSIS, SimulationStatus.FINISHED, SimulationStatus.MITOSIS])
        # TODO: read results through time and search for events
        self._log_status()

