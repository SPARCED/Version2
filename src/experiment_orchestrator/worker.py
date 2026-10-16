#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque

from pathlib import Path

from config.mpi import BROKER_RANK
from config.paths import MODELS_DIR_PATH
from config.protocol_file_format import ProtocolContextKeys

from runtime.logging import log, log_time
from runtime.performance import now

from simulation import Simulation
from simulation import SimulationStatus

from utils.path_validator import PathValidator


def worker(comm, rank, size, context):
    t_worker_start = now()
    log.info("Worker started with context: %r", context)

    # Reconstruct paths
    model_path = PathValidator.directory(MODELS_DIR_PATH / Path(context[ProtocolContextKeys.MODEL_FOLDER].lstrip("\//")))
    output_path = PathValidator.directory(model_path / Path(context[ProtocolContextKeys.OUTPUT].lstrip("\//")))

    # Deduce from rank assigned list of cells
    nb_cells = context[ProtocolContextKeys.NB_CELLS]
    nb_workers = size - 1

    cell_ids = [c for c in range(rank, nb_cells+1, nb_workers)]
    log.debug("Worker got assigned the following cells: %s", cell_ids)

    # TODO: setup solver (reading SBML is dependent on chosen solver)
    # Could still be nice to store initial state if possible

    # Build protocol (create original FIFO)
    protocol = []

    for s in context[ProtocolContextKeys.PROTOCOL]:
        step = Simulation(**s)
        protocol.append(step)
        log.debug("Worker loaded step: %s", s)

    # Perform protocol on each cell
    for cell in cell_ids:
        log.debug("Worker takes cell: %d", cell)

        protocol_queue = deque(protocol)    # WARNING: Shallow copy, always reset the objects afterwards

        while protocol_queue:
            simulation = protocol_queue.popleft()
            log.debug(f"Cell nb {cell}: started step {simulation.step_number}")
            
            try:
                # Load initial conditions
                if simulation.from_origin:
                    # Load from SBML
                    pass
                else:
                    simulation.load_initial_conditions(context[ProtocolContextKeys.PROTOCOL_NAME], output_path, cell)
                # Load modifications
                simulation.load_modifications()
                # Run
                status = simulation.run()
                if status == SimulationStatus.MITOSIS:
                    # TODO: see in your notebook how to handle daughter cells
                    log.debug("Mitosis occured")
            finally:
                simulation.reset()

    t_worker_stop = now() - t_worker_start
    log_time("worker: %f", t_worker_stop)

