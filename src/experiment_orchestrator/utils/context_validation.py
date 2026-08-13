#!usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from pathlib import Path

from config.paths import MODELS_DIR_PATH
from config.protocol_file_format import ProtocolContextKeys, PROTOCOL_REQUIRED_KEYS, VALID_SOLVER_VALUES

from utils.validation import InvalidContext, ValidationError
from utils.step_validation import validate_step


def validate_model_folder(value):
    errors = []

    model_path = MODELS_DIR_PATH / Path(value.lstrip("/\\"))

    if not model_path.exists():
        errors.append(ValidationError(str(value), "does not exist"))
    elif not model_path.is_dir():
        errors.append(ValidationError(str(value), "is not a directory"))

    return errors

def validate_nb_cells(value):
    errors = []
    
    if type(value) is not int or value <= 0:
        errors.append(ValidationError(str(value), "is not a positive integer"))

    return errors

def validate_solver(value):
    errors = []
    
    if not value in VALID_SOLVER_VALUES:
        errors.append(ValidationError(str(value), "is not a valid solver"))

    return errors

def validate_protocol(protocol):
    errors = []

    for step in protocol:
        errors.extend(validate_step(step))

    return errors

# This is more an example on how validation is implemented than a
# complete set of validation functions
FIELD_VALIDATORS = {
        ProtocolContextKeys.MODEL_FOLDER: validate_model_folder,
        ProtocolContextKeys.NB_CELLS: validate_nb_cells,
        ProtocolContextKeys.SOLVER: validate_solver,
        ProtocolContextKeys.PROTOCOL: validate_protocol
        }

# List of all the first level keys known (subkeys not included)
KNOWN_KEYS = set(ProtocolContextKeys)


def validate_context(context):
    # Context should be a dictionnary
    if not isinstance(context, dict):
        raise InvalidContext([ValidationError("context", "must be a dictionnary")])

    errors = []

    # Unknown keys are forbidden (first level - subkeys not concerned)
    for key in context:
        if key not in KNOWN_KEYS:
            errors.append(ValidationError(key, "unknown key"))

    # Required keys must be present
    for key in PROTOCOL_REQUIRED_KEYS:
        if key not in context:
            errors.append(ValidationError(key, "is missing"))

    # Validate present known keys for which a validator exists
    for key, validator in FIELD_VALIDATORS.items():
        if key in context:
            errors.extend(validator(context[key]))

    if errors:
        raise InvalidContext(errors)

