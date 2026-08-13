#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import StrEnum

# PROTOCOL FILE FORMAT CONVENTIONS

# File format extension
EXTENSION = ".yml"

# Context keys
class ProtocolContextKeys(StrEnum):
    # Paths, files, directories
    MODEL_FOLDER = "model"
    OUTPUT = "output_directory"
    PROTOCOL_NAME = "name"
    SBML = "sbml"
    # Experimental settings
    NB_CELLS = "nb_cells"
    SOLVER = "solver"
    # Protocol
    PROTOCOL = "protocol"

PROTOCOL_REQUIRED_KEYS = {
        ProtocolContextKeys.OUTPUT,
        ProtocolContextKeys.PROTOCOL_NAME,
        ProtocolContextKeys.SBML,
        ProtocolContextKeys.NB_CELLS,
        ProtocolContextKeys.SOLVER
        }

VALID_SOLVER_VALUES = {"AMICI", "BNGSim", "Rover", "SingleCell", "SPARCED", "Tellurium"}

# Step keys
class ProtocolStepKeys(StrEnum):
    DURATION = "duration"
    INPUT = "input"
    MODIFICATIONS = "modifications"
    NUMBER = "step"
    SIMULATION_MODE = "simulation_mode"

VALID_INPUT_KEYS = {"name", "origin", "timepoint"}
VALID_MODIFICATIONS_KEYS = {"compartments", "parameters", "ratelaws", "species"}

VALID_SIMULATION_MODE_VALUES = {"deterministic", "stochastic", "lineage"}
VALID_TIMEPOINT_VALUES = {"first", "last", "random"}

