#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mpi4py import MPI
from pathlib import Path

from config.mpi import BROKER_RANK

from runtime.logging import log, log_time, setup
from runtime.performance import now

from preprocessing import load_config

from broker import broker
from worker import worker


def run_experiment(
        protocol_relative_path: str | Path,
        model_relative_path: str | Path,
        logging_level: str = "INFO"):
    
    t_total_start = now()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Define logging level
    setup(logging_level, rank)

    if size < 2:
        raise RuntimeError(f"Please provide at least 2 MPI processes. Currently alloted: {size}.")
    if not (0 <= BROKER_RANK < size):
        raise RuntimeError(f"BROKER_RANK must be in [0, {size-1}].")

    if rank == 0:
        config = load_config(protocol_relative_path, model_relative_path)
    else:
        config = None

    # Broadcast configuration
    t_bcast_start = now()
    config = comm.bcast(config, root=0)
    t_bcast_stop = now() - t_bcast_start
    log_time("bcast: %f", t_bcast_stop) 

    
    if rank == BROKER_RANK:
        broker(comm, rank, size, config)
    else:
        worker(comm, rank, size, config)

    t_total_stop = now() - t_total_start
    log_time("total: %f", t_total_stop)


if __name__ == "__main__":
    run_experiment("official/test/temp.yml", "official/2027", "DEBUG")


