#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mpi4py import MPI
from pathlib import Path

from broker import broker
from worker import worker

from config import BROKER_RANK
from preprocessing import load_config
from runtime.logging import log, log_time, setup
from runtime.performance import now


def run_experiment(model_path: str | Path, experiment_name: str, logging_level: str = "INFO"):
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
        config = load_config()
    else:
        config = None

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
    run_experiment("../path/to/model", "experiment_name", "DEBUG")

