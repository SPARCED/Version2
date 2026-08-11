#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import StrEnum

# PROTOCOL FILE FORMAT CONVENTIONS

# File format extension
EXTENSION = ".yml"

# Context keys
class ProtocolContextKeys(StrEnum):
    MODEL_FOLDER = "model"
    NB_CELLS = "nb_cells"
    OUTPUT = "output_directory"
    PROTOCOL = "protocol"
    PROTOCOL_NAME = "name"
    SBML = "sbml"
    SOLVER = "solver"

PROTOCOL_REQUIRED_KEYS = {
        ProtocolContextKeys.NB_CELLS,
        ProtocolContextKeys.PROTOCOL,
        ProtocolContextKeys.SBML,
        ProtocolContextKeys.SOLVER
        }

