#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.mpi import BROKER_RANK

from runtime.logging import log


def broker(comm, rank, size, context):
    log.info("Broker started")
    log.debug("Config: %r", context)

