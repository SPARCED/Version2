#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

with open("../legacy/Species.txt", newline="", encoding="utf-8") as fin, \
     open("../data/species.tsv", "w", newline="", encoding="utf-8") as fout:

    reader = csv.DictReader(fin, delimiter="\t")
    writer = csv.writer(fout, delimiter="\t")

    writer.writerow([
        "speciesId",
        "compartment",
        "type",
        "initialConcentration",
        "solver",
        "annotation",
    ])

    for row in reader:

        annotations = []

        ensembl = row["Annotation_ENSEMBL"].split()
        hgnc = row["Annotation_HGNC"].split()

        annotations.extend(ensembl)
        annotations.extend(hgnc)

        writer.writerow([
            row["species"],                # -> speciesId
            row["compartment"],
            "Undefined",                   # type
            row["IC_Xinitialized"],        # -> initialConcentration
            "Undefined",                   # solver
            ",".join(annotations),         # annotations
        ])
