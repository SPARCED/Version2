#!usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from config.protocol_file_format import PROTOCOL_REQUIRED_KEYS

from runtime.logging import log


@dataclass
class ValidationError:
    field: str
    message: str


class InvalidContext(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Protocol validation failed with {len(errors)} error(s).")


def validate_required_keys(context):
    errors = []

    for key in PROTOCOL_REQUIRED_KEYS:
        if key not in context:
            errors.append(ValidationError(key, "is missing"))

    return errors


VALIDATORS = (
        validate_required_keys,
        )


def validate_context(context):
    if not isinstance(context, dict):
        raise InvalidContext([ValidationError("context", "must be a dictionnary")])

    errors = []

    for validator in VALIDATORS:
        errors.extend(validator(context))

    if errors:
        raise InvalidContext(errors)

