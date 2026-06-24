#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from config.in_house_file_format import PARAMETERS_COLUMNS


@dataclass
class Parameter:
    id: str
    value: float

    @classmethod
    def from_row(cls, row):
        c = PARAMETERS_COLUMNS
        return cls(
                id=row[c["parameterId"]],
                value=float(row[c["nominalValue"]])
                )

