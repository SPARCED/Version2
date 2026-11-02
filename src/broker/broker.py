#!/usr/bin/env python
# -*- coding: utf-8 -*-

from broker.runtime.logging import log


def broker(comm, rank, size, protocol):
    log.info("Broker started")
    log.debug("Config: %r", protocol)

