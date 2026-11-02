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


class ColorFormatter(logging.Formatter):
    COLORS = {
            logging.DEBUG:      "\033[0m",      # Default
            TIME:               "\033[32m",     # Green
            logging.INFO:       "\033[0m",      # Default
            logging.WARNING:    "\033[33m",     # Yellow
            logging.ERROR:      "\033[1;31m",   # Bold red
            logging.CRITICAL:   "\033[1;31m",   # Bold red
            }

    RESET = "\033[0m"

    def format(self, record):
        message = super().format(record)
        color = self.COLORS.get(record.levelno)

        if color:
            return f"{color}{message}{self.RESET}"

        return message


def log_time(msg, *args):
    log.log(TIME, msg, *args)

def setup(level: str = "INFO", rank: int | None = None) -> None:
    prefix = ""

    if rank is not None:
        prefix = f"[R{rank:03d}]"

    handler = logging.StreamHandler()
    handler.setFormatter(
            ColorFormatter(f"{prefix} [%(levelname)-8s] %(message)s")
            )
    
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(LEVELS[level.upper()])


log = logging.getLogger(__name__)

