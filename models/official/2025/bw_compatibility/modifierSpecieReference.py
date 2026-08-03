#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import re


ID_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
FUNCTIONS = {"exp", "log", "ln", "pow", "sqrt", "sin", "cos", "tan", "abs"}

COLUMNS = {
        "id": 0,
        "compartment": 1,
        "equation": 2,
        "formula": 3
        }


def species_from_equation(eq):
    species = set()
    for part in re.split(r"=>|<=>|->|\+", eq):
        part = part.strip()
        if not part:
            continue
        # Handle coeffiecients
        part = re.sub(r"^\d+(\.\d+)?\s*\*\s*", "", part)
        species.add(part)
    return species

def extract_modifiers(eq, formula):
    species = species_from_equation(eq)
    ids = set(ID_RE.findall(formula))
    return sorted(
        x for x in ids
        if x not in species
        and not x.startswith(("k", "v"))
        and x not in FUNCTIONS
    )


if __name__ == "__main__":
    old_file = Path("../data/intermediary_ratelaws.tsv")
    new_file = Path("../data/ratelaws.tsv")
    
    if not old_file.exists() or not old_file.is_file():
        raise ValueError(f"Invalid path")
    
    with old_file.open("r", encoding="utf-8") as fin, new_file.open("w", encoding="utf-8") as fout:
        header = next(fin)
        fout.write(header)

        for line in fin:
            parts = line.strip().split("\t")
            id=parts[COLUMNS["id"]]
            compartment=parts[COLUMNS["compartment"]]
            equation=parts[COLUMNS["equation"]]
            formula=parts[COLUMNS["formula"]]
            modifiers = extract_modifiers(equation, formula)
            modifiers_str = f" [{','.join(modifiers)}]" if modifiers else ""
            fout.write(f"{id}\t{compartment}\t{equation} {modifiers_str}\t{formula}\n")

