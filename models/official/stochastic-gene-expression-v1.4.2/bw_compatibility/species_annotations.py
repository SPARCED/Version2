#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd


annotations = pd.read_csv("../legacy/SPARCED-Annotations-v142.tsv", sep="\t")
species = pd.read_csv("../legacy/SPARCED-Species-v142.tsv", sep="\t")

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
        "initialConcentration (nM)",
        "solver",
        "annotation"
    ]
]

result.to_csv("../data/species.tsv", sep="\t", index=False)

