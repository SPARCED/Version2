#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from config.paths import MODELS_DIR_PATH
from config.protocol_file_format import ProtocolContextKeys

from broker.runtime.logging import log, log_time
from broker.runtime.performance import now

from validators.path import PathValidator

"""
from types import SimpleNamespace

from collections import deque
from copy import deepcopy

from simulation._load_solver import load_solver
from simulation.step import SimulationStep
from simulation.step import SimulationStatus
"""

def worker(comm, rank, size, context):
    t_worker_start = now()
    log.info("Worker started with context: %r", context)

    # Reconstruct paths
    model_path = PathValidator.directory(MODELS_DIR_PATH / Path(context[ProtocolContextKeys.MODEL_FOLDER].lstrip("\//")))
    output_path = PathValidator.directory(model_path / Path(context[ProtocolContextKeys.OUTPUT_FOLDER].lstrip("\//")))
    sbml_paths = [PathValidator.file(model_path / sbml_file.lstrip("\//")) for sbml_file in context[ProtocolContextKeys.SBML_FILES]]

    # Deduce from rank assigned list of cells
    nb_cells = context[ProtocolContextKeys.NB_CELLS]
    nb_workers = size - 1

    cell_ids = [c for c in range(rank, nb_cells+1, nb_workers)]
    log.debug(f"Worker got assigned the following cells: {cell_ids}")

    # Setup solver
    solver_class = load_solver(context[ProtocolContextKeys.SOLVER])
    args = SimpleNamespace(model_paths=sbml_paths)
    solver = solver_class(args)
    # Load SBML
    # WARNING: by default, the wrappers consider the first file as deterministic and the second as stochastic.
    # This implicit behavior should either be corrected or documented.
    solver.load(args)
    # Could still be nice to store initial state if possible

    # Build protocol (create original FIFO)
    protocol = []

    for s in context[ProtocolContextKeys.PROTOCOL]:
        step = SimulationStep(s, context[ProtocolContextKeys.PROTOCOL_NAME], 0)
        protocol.append(step)
        log.debug("Worker loaded step: %s", s)

    lineage_tracing = {}

    # Perform protocol on each cell
    for cell in cell_ids:
        log.debug("Worker takes cell: %d", cell)
        
        if cell > nb_cells:
            log.debug("Lineage tracing is not implemented yet.")
            continue

        protocol_queue = deque(protocol)    # WARNING: Shallow copy, always reset the objects afterwards

        while protocol_queue:
            simulation = protocol_queue.popleft()
            log.debug(f"Cell nb {cell}: started step {simulation.infos.step}")
            
            try:
                # Load initial conditions
                if simulation.is_from_origin:
                    # Load from SBML
                    pass
                else:
                    simulation.load_initial_conditions(context[ProtocolContextKeys.PROTOCOL_NAME], output_path, cell)
                # Load modifications
                simulation.load_modifications(solver)
                # Run
                result_path = output_path / f"{context[ProtocolContextKeys.PROTOCOL_NAME]}_step_{simulation.infos.step}_cell_{cell}.tsv"
                status = simulation.run(solver, result_path)
                # Apoptosis - Empty queue, as the next protocol steps are not applicable anymore
                if status ==  SimulationStatus.APOPTOSIS:
                    protocol_queue.clear()
                # Mitosis - Add daughter cell ids to list of cell to simulate
                # In case of lineage tracing, because otherwise the cell simulation just stops I guess?
                if status == SimulationStatus.MITOSIS:
                    daughter_1 = cell + pow(2, simulation.generation)*nb_cells
                    daughter_2 = cell + pow(2, simulation.generation+1)*nb_cells
                    # TODO: there are some updates to do on the copies, especially the generation and input data
                    lineage_tracing[daughter_1] = deepcopy(protocol_queue)
                    lineage_tracing[daughter_2] = deepcopy(protocol_queue)
                    # To remove later as the dictionnary should be sufficient to handle lineage tracing
                    cell_ids.append(daughter_1)
                    cell_ids.append(daughter_2)
            finally:
                simulation.reset()

    t_worker_stop = now() - t_worker_start
    log_time("worker: %f", t_worker_stop)

