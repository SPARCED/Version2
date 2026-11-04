#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from types import SimpleNamespace

from config.paths import MODELS_DIR_PATH
from config.protocol_file_format import ProtocolContextKeys

from validators.path import PathValidator

from broker.runtime.logging import log, log_time
from broker.runtime.performance import now

from broker.utils.protocol import load_protocol, run_protocol
from broker.utils.worker import compute_assigned_cell_ids

from solvers.loader import load_solver_cls


def worker(comm, rank, size, context):
    t_worker_start = now()
    log.info(f"Worker started with context: {context}")

    # Reconstruct paths
    model_path = PathValidator.directory(MODELS_DIR_PATH / Path(context[ProtocolContextKeys.MODEL_FOLDER].lstrip("/\\")))
    output_path = PathValidator.directory(model_path / Path(context[ProtocolContextKeys.OUTPUT_FOLDER].lstrip("/\\")))
    sbml_paths = [PathValidator.file(model_path / sbml_file.lstrip("/\\")) for sbml_file in context[ProtocolContextKeys.SBML_FILES]]

    # Setup solver
    try:
        SolverClass = load_solver_cls(context[ProtocolContextKeys.SOLVER])
    except Exception as e:  # Most likely raised by an error when loading the solver
        log.critical(e)
        comm.Abort(1)       # This kills the whole computation, including other ranks.
                            # Reading documentation about "ULFM" (User-Level Failure Mitigation) could be interesting.
    args = SimpleNamespace(model_paths=sbml_paths)
    solver = SolverClass(args)

    # Load SBML file(s) within solver
    # TODO: By default, the wrappers consider the first file as deterministic, and the second as stochastic.
    #       This implicit behavior should either be corrected, or documented.
    solver.load(args)

    # Build protocol (create original FIFO)
    protocol = load_protocol(context)
    
    # Deduce from rank assigned list of cells
    cell_ids = compute_assigned_cell_ids(context[ProtocolContextKeys.NB_CELLS], rank, size)
    log.debug(f"Worker got assigned the following cells: {cell_ids}.")

    # Perform protocol on each cell
    nb_cells = context[ProtocolContextKeys.NB_CELLS]
    lineage_tracing = {}

    for cell in cell_ids:
        log.debug(f"Worker takes cell: {cell}")
        
        if cell > nb_cells:
            log.debug("Lineage tracing is not implemented yet.")
            continue
            # TODO: extract protocol from lineage_tracing dictionnary
        
        run_protocol(protocol, cell, solver, output_path)
    
    t_worker_stop = now() - t_worker_start
    log_time("worker: %f", t_worker_stop)

