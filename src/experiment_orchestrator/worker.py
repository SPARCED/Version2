#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque

from config.mpi import BROKER_RANK
from config.protocol_file_format import ProtocolContextKeys

from runtime.logging import log, log_time
from runtime.performance import now

from simulation import Simulation


def worker(comm, rank, size, context):
    t_worker_start = now()

    log.info("Worker started")
    log.debug("Context: %r", context)

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
        log.debug("Worker loads step: %s", s)
        step = Simulation(**s)
                # protocol_name=context[ProtocolContextKeys.PROTOCOL_NAME])
                # output=context[ProtocolContextKeys.OUTPUT_DIR, # a bit more
                # solver=context[ProtocolContextKeys.SOLVER])
        protocol.append(step)
        log.debug("Worker loaded step: %s", s)

    # Per cell tasks
    # Handle the FIFO
    # Read next cell task ans launch simulator
    # Handle simulator output if necessary

    for cell in cell_ids:
        log.debug("Worker takes cell: %d", cell)

        protocol_queue = deque(protocol)    # WARNING: Shallow copy, always reset the objects afterwards

        while protocol_queue:
            simulation = protocol_queue.popleft()
            #simulation.revolve_some_stuff() # Cell number, effectively grab the data
            #simulation.run()    # Save included, every 100 timepoints
            #status = simulation.status()
            # if status blablabla -> queue.append()
            # simulation.reset() !!! try finally

    t_worker_stop = now() - t_worker_start
    log_time("worker: %f", t_worker_stop)

