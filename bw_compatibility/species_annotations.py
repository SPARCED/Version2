#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd


annotations = pd.read_csv("../models/official/2027/data/SPARCED/annotations.tsv", sep="\t")
species = pd.read_csv("../models/official/2027/data/SPARCED/species.tsv", sep="\t")

annotations_grouped = (
    annotations
    .groupby("speciesId")
    .agg({
        "type": "first",
        "annotation": ",".join
    })
    .reset_index()
)

result = species.merge(
    annotations_grouped,
    on="speciesId",
    how="left"
)

result = result[
    [
        "speciesId",
        "compartment",
        "type",
        "initialConcentration",
        "solver",
        "annotation"
    ]
]

result.to_csv("../models/official/2027/data/SPARCED/species_with_annotations.tsv", sep="\t", index=False)

