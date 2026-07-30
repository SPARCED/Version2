#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import StrEnum

# PROTOCOL FILE FORMAT CONVENTIONS

# File format extension
EXTENSION = ".yml"

# Context keys
class ProtocolContextKeys(StrEnum):
    NB_CELLS = "nb_cells"

PROTOCOL_REQUIRED_KEYS = {
        ProtocolContextKeys.NB_CELLS
        }

