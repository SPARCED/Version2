#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import re


PARAM_RE = re.compile(r"(?<![A-Za-z0-9_])k[A-Za-z0-9]+(?:_\d+)?")
NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?$")


known_parameters = set()

with open("../legacy/Ratelaws.txt", newline="", encoding="utf-8") as fin, \
     open("../data/parameters.tsv", "w", newline="", encoding="utf-8") as fout:

    reader = csv.reader(fin, delimiter="\t")
    writer = csv.writer(fout, delimiter="\t")

    writer.writerow(["reactionId", "parameterId", "parameterScale", "lowerBound", "upperBound", "nominalValue", "estimate"])

    header = next(reader)

    reaction_idx = header.index("Rxn_name")
    ratelaw_idx = header.index("Ratelaw")

    for row in reader:
        reaction = row[reaction_idx]
        ratelaw = row[ratelaw_idx].strip()

        values = [v.strip() for v in row[ratelaw_idx + 1:] if v.strip()]

        # Constant as ratelaw
        if NUMBER_RE.fullmatch(ratelaw):
            parameter = f"k{reaction}"

            if parameter not in known_parameters:
                writer.writerow([reaction, parameter, "lin", ratelaw, ratelaw, ratelaw, 0])
                known_parameters.add(parameter)

            continue

        parameters = list(dict.fromkeys(PARAM_RE.findall(ratelaw)))

        if len(parameters) != len(values):
            raise ValueError(
                f"{reaction}: found {len(parameters)} parameters "
                f"but {len(values)} values.\n"
                f"Ratelaw: {ratelaw}\n"
                f"Parameters: {parameters}\n"
                f"Values: {values}"
            )

        for parameter, value in zip(parameters, values):
            if parameter not in known_parameters:
                writer.writerow([reaction, parameter, "lin", value, value, value, 0])
                known_parameters.add(parameter)
