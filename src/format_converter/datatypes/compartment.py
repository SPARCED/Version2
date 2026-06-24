#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from config.in_house_file_format import COMPARTMENTS_COLUMNS


@dataclass
class Compartment:
    id: str
    value: float
    annotation: str

    @classmethod
    def from_row(cls, row):
        c = COMPARTMENTS_COLUMNS
        return cls(
                id=row[c["compartment"]],
                value=float(row[c["volume"]]),
                annotation=row[c["annotation"]]
                )

