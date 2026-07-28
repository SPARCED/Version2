#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


TIME = 15
logging.addLevelName(TIME, "TIME")

LEVELS = {
        "DEBUG": logging.DEBUG,
        "TIME": TIME,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
        }


def log_time(msg, *args):
    log.log(TIME, msg, *args)

def setup(level: str = "INFO", rank: int | None = None) -> None:
    prefix = ""

    if rank is not None:
        prefix = f"[R{rank:03d}]"

    logging.basicConfig(
            level = getattr(logging, level.upper()),
            format = f"{prefix} [%(levelname)-8s] %(message)s"
            )


log = logging.getLogger(__name__)

