#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import re

df = pd.read_csv("../legacy/Ratelaws.txt", sep="\t")    # Ratelaws
stoic = pd.read_csv("../legacy/StoicMat.txt", sep="\t", index_col=0) # StoicMat
params = pd.read_csv("../data/parameters.tsv", sep="\t")    # Clean parameters


# StoicMat to equation
def build_equation(reaction):
    if reaction not in stoic.columns:
        print(f"{reaction} not found")
        return ""

    col = stoic[reaction]

    reactants = []
    products = []
    
    for species, coeff in col.items():
        coeff = float(coeff)
        if coeff == 0:
            continue
        
        species = str(species)

        if coeff < 0:
            n = abs(coeff)
            reactants.append(species if n == 1 else f"{n:g} {species}")
        else:
            products.append(species if coeff == 1 else f"{coeff:g} {species}")
    
    left = " + ".join(reactants)
    right =" + ".join(products)
    return f"{left} => {right}"

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

def build_mass_action_formula(reaction):
    if reaction not in stoic.columns:
        return ""

    # Get parameter name
    param = params.loc[params["reactionId"] == reaction, "parameterId"]

    if len(param) == 0:
        print(f"No parameter found for {reaction}")
        return ""

    parameter_id = param.iloc[0]

    terms = [str(parameter_id)]

    for species, coeff in stoic[reaction].items():
        coeff = int(coeff)

        if coeff < 0:
            for _ in range(abs(coeff)):
                terms.append(str(species))

    return " * ".join(terms)


output = pd.DataFrame({
    "reactionId": df["Rxn_name"],
    "compartment": df["Comp_correction"],
    "equation": df["Rxn_name"].apply(build_equation),
    "formula": df["Ratelaw"]
})

output["formula"] = output.apply(
    lambda row: build_mass_action_formula(row["reactionId"])
    if re.fullmatch(r"\s*[+-]?\d*\.?\d+([eE][+-]?\d+)?\s*", str(row["formula"]))
    else row["formula"],
    axis=1
)


output.to_csv("../data/intermediary_ratelaws.tsv", sep="\t", index=False)

