#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import BROKER_RANK
from runtime.logging import log


def worker(comm, rank, size, config):
    log.info("Worker started")
    log.debug("Config: %r", config)

    # Read nb cells from config file

    nb_workers = size - 1
    for task_id in range(rank, 10, nb_workers):
        log.debug("Worker takes cell: %d", task_id)

