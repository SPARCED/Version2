#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from config.in_house_file_format import RATELAWS_COLUMNS


@dataclass
class Ratelaw:
    id: str
    compartment: str
    equation: str
    formula: str

    @classmethod
    def from_row(cls, row):
        c = RATELAWS_COLUMNS
        return cls(
                id=row[c["reactionId"]],
                compartment=row[c["compartment"]],
                equation=row[c["equation"]],
                formula=row[c["ratelaw"]]
                )

