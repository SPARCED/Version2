#!usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any


class InvalidContext(Exception):
    def __init__(self, errors):
        self.errors = errors
        details = "\n".join(f"- {error}" for error in errors)
        super().__init__(f"Protocol validation failed with {len(errors)} error(s):\n{details}")

@dataclass
class ValidationError:
    field: str
    message: str
    value: Any = None

    def __str__(self):
        if self.value is None:
            return f"{self.field}: {self.message}"
        return f"{self.field}: {self.message} (value={self.value!r})"

