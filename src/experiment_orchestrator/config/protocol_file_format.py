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

# Context values
# TODO: replace with SIMULATOR_REGISTRY
VALID_SOLVER_VALUES = {"AMICI", "BNGSim", "Rover", "SingleCell", "SPARCED", "Tellurium"}

# Step keys
class ProtocolStepKeys(StrEnum):
    DURATION = "duration"
    EXCHANGE = "exchange"
    INPUT = "input"
    MODIFICATIONS = "modifications"
    NAME = "name"
    NUMBER = "step"
    SIMULATION_MODE = "simulation_mode"

VALID_INPUT_KEYS = {"name", "origin", "timepoint"}
VALID_MODIFICATIONS_KEYS = {"compartments", "parameters", "ratelaws", "species"}

STEP_REQUIRED_KEYS = {
        ProtocolStepKeys.DURATION,
        ProtocolStepKeys.SIMULATION_MODE
        }

# Step values
DefaultStepValues = {
        ProtocolStepKeys.EXCHANGE: 30,
        ProtocolStepKeys.INPUT: {},
        ProtocolStepKeys.MODIFICATIONS: {},
        ProtocolStepKeys.NAME: None,
        ProtocolStepKeys.NUMBER: None
        }

# Origin value reserved for reloading from SBML
RESERVED_ORIGIN_VALUE = 0

VALID_SIMULATION_MODE_VALUES = {"deterministic", "stochastic", "lineage"}

# Timepoint values
class ProtocolTimepointValues(StrEnum):
    FIRST = "first"
    LAST = "last"
    RANDOM = "random"

VALID_TIMEPOINT_VALUES = {
        ProtocolTimepointValues.FIRST,
        ProtocolTimepointValues.LAST,
        ProtocolTimepointValues.RANDOM
        }

