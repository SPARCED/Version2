#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import StrEnum

# IN-HOUSE FILE FORMAT CONVENTIONS

# File format extension
EXTENSION = ".tsv"

# Files names
class InHouseFilesNames(StrEnum):
    ANNOTATIONS = "annotations",
    COMPARTMENTS = "compartments",
    PARAMETERS = "parameters",
    RATELAWS = "ratelaws",
    SPECIES = "species"

# Files structure
COMPARTMENTS_COLUMNS = {
        "compartment": 0,
        "volume": 1,
        "annotation": 2,
        "fieldId": 3
        }

PARAMETERS_COLUMNS = {
        "reactionId": 0,
        "parameterId": 1,
        "parameterScale": 2,
        "lowerBound": 3,
        "upperBound": 4,
        "nominalValue": 5,
        "estimate": 6
        }

RATELAWS_COLUMNS = {
        "reactionId": 0,
        "compartment": 1,
        "equation": 2,
        "formula": 3
        }

SPECIES_COLUMNS = {
        "speciesId": 0,
        "compartment": 1,
        "initialConcentration": 2,
        "solver": 3
        }

