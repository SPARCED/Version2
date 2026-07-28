#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mpi4py import MPI

from config import BROKER_RANK


def worker(comm, rank, size, config):
    print(f"Hello from worker {rank}! I have config: {config}")

    # Read nb cells from config file

    nb_workers = size - 1
    for task_id in range(rank, 10, nb_workers):
        print(f"Worker {rank} executes task {task_id}.")

