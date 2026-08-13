#!usr/bin/env python
# -*- coding: utf-8 -*-

from config.protocol_file_format import ProtocolStepKeys, VALID_INPUT_KEYS, VALID_MODIFICATIONS_KEYS, VALID_SIMULATION_MODE_VALUES, VALID_TIMEPOINT_VALUES

from utils.validation import ValidationError


def validate_step_duration(value):
    errors = []

    if type(value) is not int or value <= 0:
        errors.append(ValidationError("duration", "is not a positive integer", value))

    return errors

def validate_step_input(value):
    errors = []

    unknown = set(value) - VALID_INPUT_KEYS
    if unknown:
        errors.append(ValidationError(unknown, "unknown input key"))
    if "timepoint" in value and not value["timepoint"] in VALID_TIMEPOINT_VALUES:
        errors.append(ValidationError("timepoint", "is not a valid timepoint", value["timepoint"]))

    return errors

def validate_step_modifications(value):
    errors = []

    if value is not None:
        for key in value:
            if key not in VALID_MODIFICATIONS_KEYS:
                errors.append(ValidationError(key, "unknown modifications key"))

    return errors

def validate_step_simulation_mode(value):
    errors = []

    if value not in VALID_SIMULATION_MODE_VALUES:
        errors.append(ValidationError("simulation mode", "is not a valid simulation mode", value))

    return errors

def validate_step_number(value):
    errors = []

    if type(value) is not int or value <= 0:
        errors.append(ValidationError("step number", "is not a positive integer", value))

    return errors


FIELD_VALIDATORS = {
    ProtocolStepKeys.DURATION: validate_step_duration,
    ProtocolStepKeys.INPUT: validate_step_input,
    ProtocolStepKeys.MODIFICATIONS: validate_step_modifications,
    ProtocolStepKeys.NUMBER: validate_step_number,
    ProtocolStepKeys.SIMULATION_MODE: validate_step_simulation_mode
    }


def validate_step(step):
    errors = []

    # Step should be a dictionnary
    if not isinstance(step, dict):
        errors.append(ValidationError("step", "is not a dictionnary", step))
        return errors

    # Validate keys for which a validator exists
    for key, validator in FIELD_VALIDATORS.items():
        if key in step:
            errors.extend(validator(step[key]))

    return errors

