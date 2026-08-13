#!usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass


class InvalidContext(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Protocol validation failed with {len(errors)} error(s).")

@dataclass
class ValidationError:
    field: str
    message: str

