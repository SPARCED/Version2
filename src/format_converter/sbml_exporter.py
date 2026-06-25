#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from sbmlutils.io import read_sbml, write_sbml, validate_sbml

from sbmlutils.factory import *
from sbmlutils.metadata import *

from utils.path_validator import PathValidator

import datatypes as in_house
from data_storage import DataStorage


class U(Units):
    nM=UnitDefinition("nM", "nanomole/litre")
    substance=UnitDefinition("substance", "nanomole")
    time=UnitDefinition("time", "second")
    volume=UnitDefinition("volume", "litre")


class SBMLExporter:
    def __init__(self, root_path: str | Path):
        self.root_path = PathValidator.directory(root_path)

    def _to_sbmlutils_compartment(self, c: in_house.Compartment) -> Compartment:
        annotation = getattr(c, "annotation", None)
        return Compartment(
                annotations = [(BQB.IS, f"go/{annotation}")] if annotation else [],
                sid=getattr(c, "id", None),
                unit=U.volume,
                value=getattr(c, "value", None))

    def _to_sbmlutils_parameters(self, p: in_house.Parameter) -> Parameter:
        return Parameter(
                sid=getattr(p, "id", None),
                value=getattr(p, "value", None))
    
    def _to_sbmlutils_reactions(self, r: in_house.Reaction) -> Reaction:
        return Reaction(
                sid=getattr(r, "id", None),
                equation=getattr(r, "equation", None),
                formula=("(" + getattr(r, "formula", None)+")*"
                    + getattr(r, "compartment", None) , None)
                )
    
    def _to_sbmlutils_species(self, s: in_house.Specie) -> Species:
        return Species(
                sid=getattr(s, "id", None),
                initialConcentration=getattr(s, "initial_concentration", None),
                compartment=getattr(s, "compartment", None),
                hasOnlySubstanceUnits=False)

    def to_sbml(self, data: DataStorage):
        model = Model(
                "debug_model",
                name="Debug Model",
                units=U,
                model_units=ModelUnits(
                    time=U.time,
                    substance=U.substance,
                    volume=U.volume),
                compartments = [self._to_sbmlutils_compartment(c) for c in data.compartments],
                species = [self._to_sbmlutils_species(s) for s in data.species],
                parameters = [self._to_sbmlutils_parameters(p) for p in data.parameters],
                reactions = [self._to_sbmlutils_reactions(r) for r in data.ratelaws]
                )
        results = create_model(
                model=model,
                filepath=Path(self.root_path) / f"{model.sid}.xml",
                validation_options=ValidationOptions(units_consistency=False),
                sbml_level=3,
                sbml_version=2)
        doc = read_sbml(source=results.sbml_path, validate=False)
        sbml = write_sbml(doc)
        print(sbml)

