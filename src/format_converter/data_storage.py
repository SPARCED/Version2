#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from config.in_house_file_format import InHouseFilesNames

from datatypes import Compartment, Parameter, Specie


class DataStorage:
    def __init__(self):
        self.compartments: list[Compartment] = []
        self.parameters: list[Parameter] = []
        self.species: list[Specie] = []

        self._loaders = {
                InHouseFilesNames.COMPARTMENTS: self._add_compartment,
                InHouseFilesNames.PARAMETERS: self._add_parameter,
                InHouseFilesNames.SPECIES: self._add_specie
                }

    def _add_compartment(self, parts: list[str]) -> None:
        self.compartments.append(Compartment.from_row(parts))

    def _add_parameter(self, parts: list[str]) -> None:
        self.parameters.append(Parameter.from_row(parts))

    def _add_specie(self, parts: list[str]) -> None:
        # TODO solver
        self.species.append(Specie.from_row(parts))

    def load_in_house_files(self, files: dict[str, list[str | Path]]) -> None:
        for file_type, paths in files.items():
            loader = self._loaders.get(file_type)   # Get loader corresponding to file type

            if loader is not None:
                for file in paths:
                    file = Path(file)

                    if not file.exists() or not file.is_file():
                        raise ValueError(f"Invalid path")

                    with file.open("r", encoding="utf-8") as f:
                        next(f)     # Skip header
                        for line in f:
                            parts=line.strip().split("\t")
                            loader(parts)

