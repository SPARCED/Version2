#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import StrEnum, auto


class SimulationStatus(StrEnum):
    INITIAL = auto()
    LOADED = auto()
    MODIFIED = auto()
    RUNNING = auto()
    SIMULATED = auto()
    APOPTOSIS = auto()
    FINISHED = auto()
    MITOSIS = auto()

