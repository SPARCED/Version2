#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mpi4py import MPI
from pathlib import Path

from config.mpi import BROKER_RANK, RANKS_MINIMUM

from broker.runtime.logging import log, log_time, setup
from broker.runtime.performance import now

from broker.preprocessing import load_protocol

from broker.broker import broker
from broker.worker import worker


def run_experiment(
        protocol_relative_path: str | Path,
        logging_level: str = "INFO"):

    t_total_start = now()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Define logging level
    setup(logging_level, rank)

    try:
        if size < RANKS_MINIMUM:
            raise RuntimeError(f"Please provide at least {RANKS_MINIMUM} MPI processes. Currently alloted: {size}.")
        if not BROKER_RANK == 0:        # Hard-coded value because users shouldn't try to change it within settings
            raise RuntimeError(f"BROKER_RANK must be 0.")
    except Exception as e:  # Most likely raised by an invalid configuration
        log.critical(e)
        comm.Abort(1)

    try:
        if rank == BROKER_RANK:
            protocol = load_protocol(protocol_relative_path)
        else:
            protocol = None
    except Exception as e:  # Most likely raised by an invalid protocol
        log.critical(e)
        comm.Abort(1)

    # Broadcast protocol
    t_bcast_start = now()
    protocol = comm.bcast(protocol, root=BROKER_RANK)
    t_bcast_stop = now() - t_bcast_start
    log_time("bcast: %f", t_bcast_stop)

    
    if rank == BROKER_RANK:
        broker(comm, rank, size, protocol)
    else:
        worker(comm, rank, size, protocol)

    t_total_stop = now() - t_total_start
    log_time("total: %f", t_total_stop)

