#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import BROKER_RANK
from runtime.logging import log, log_time
from runtime.performance import now

def worker(comm, rank, size, config):
    t_worker_start = now()

    log.info("Worker started")
    log.debug("Config: %r", config)

    # Read nb cells from config file

    nb_workers = size - 1
    for task_id in range(rank, 10, nb_workers):
        log.debug("Worker takes cell: %d", task_id)

    t_worker_stop = now() - t_worker_start
    log_time("worker: %f", t_worker_stop)

