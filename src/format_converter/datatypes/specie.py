#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from config.in_house_file_format import SPECIES_COLUMNS


@dataclass
class Specie:
    id: str
    compartment: str
    initial_concentration: float

    @classmethod
    def from_row(cls, row):
        c = SPECIES_COLUMNS
        return cls(
                id=row[c["speciesId"]],
                compartment=row[c["compartment"]],
                initial_concentration=float(row[c["initialConcentration"]])
                )

