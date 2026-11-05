#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from pathlib import Path
from typing import Any

from config.protocol_file_format import ProtocolContextKeys

from broker.runtime.logging import log

from broker.simulation_status import SimulationStatus
from broker.simulation_step import SimulationStep

from solvers._abstract_solver import AbstractSolver


def load_protocol(context: dict[str, Any]) -> list[SimulationStep]:
    protocol = []

    for s in context[ProtocolContextKeys.PROTOCOL_DETAILS]:
        step = SimulationStep(s, context[ProtocolContextKeys.PROTOCOL_NAME])
        protocol.append(step)

    return protocol

def run_protocol(protocol: list[SimulationStep], cell_id: int, solver: AbstractSolver, output_path: str | Path, args):
    protocol_queue = deque(protocol)    # WARNING: Shallow copy, always reset the objects afterwards

    while protocol_queue:
        simulation = protocol_queue.popleft()

        try:
            # Load protocol
            if simulation.is_from_origin:
                solver.load(args)
            else:
                log.critical("Loading not implemented yet.")
            # Apply modifications
            simulation.apply_modifications(solver)
            # Run
            status = simulation.run(cell_id, solver, output_path)
        finally:
            # Reset
            simulation.reset()

