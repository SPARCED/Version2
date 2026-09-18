#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from config.in_house_file_format import SPECIES_COLUMNS


@dataclass
class Specie:
    id: str
    compartment: str
    initial_concentration: float
    annotations: list[str]

    @classmethod
    def from_row(cls, row):
        c = SPECIES_COLUMNS

        if c["annotation"] < len(row):
            annotation = [a.strip() for a in row[c["annotation"]].split(",") if a.strip()]
        else:
            annotation = []

        return cls(
                id=row[c["speciesId"]],
                compartment=row[c["compartment"]],
                initial_concentration=float(row[c["initialConcentration"]]),
                annotations=annotation
                )

