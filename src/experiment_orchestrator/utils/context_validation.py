#!usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from config.protocol_file_format import ProtocolContextKeys, PROTOCOL_REQUIRED_KEYS

from runtime.logging import log


@dataclass
class ValidationError:
    field: str
    message: str


class InvalidContext(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Protocol validation failed with {len(errors)} error(s).")


def validate_model_folder(value):
    errors = []
    return errors

def validate_output(value):
    errors = []
    return errors

def validate_protocol_name(value):
    errors = []
    return errors

def validate_sbml(value):
    errors = []
    return errors

def validate_nb_cells(value):
    errors = []
    return errors

def validate_solver(value):
    errors = []
    return errors

def validate_protocol(value):
    errors = []
    return errors


FIELD_VALIDATORS = {
        ProtocolContextKeys.MODEL_FOLDER: validate_model_folder,
        ProtocolContextKeys.OUTPUT: validate_output,
        ProtocolContextKeys.PROTOCOL_NAME: validate_protocol_name,
        ProtocolContextKeys.SBML: validate_sbml,
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

