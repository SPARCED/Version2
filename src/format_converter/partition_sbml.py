#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Partition a One4All SBML model into stochastic and deterministic submodels."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import libsbml
import pandas as pd

logger = logging.getLogger(__name__)

# SBML SIds: letters, digits, underscore; must not start with a digit.
_INVALID_SID_CHARS = re.compile(r"[^A-Za-z0-9_]")


def sanitize_model_id(model_id: str) -> str:
    """Return a valid SBML SId (hyphens and other punctuation → underscores)."""
    cleaned = _INVALID_SID_CHARS.sub("_", str(model_id).strip())
    if not cleaned:
        cleaned = "model"
    if cleaned[0].isdigit():
        cleaned = f"m_{cleaned}"
    return cleaned


@dataclass
class PartitionResult:
    stochastic_path: Path
    deterministic_path: Path
    stochastic_reaction_ids: set[str]
    deterministic_reaction_ids: set[str]
    stochastic_species_ids: set[str]
    deterministic_species_ids: set[str]
    stochastic_parameter_ids: set[str]
    deterministic_parameter_ids: set[str]


@dataclass
class VerificationReport:
    ok: bool
    messages: list[str]

    def raise_if_failed(self) -> None:
        if not self.ok:
            raise AssertionError("\n".join(self.messages))


def _ids(list_of) -> set[str]:
    return {obj.getId() for obj in list_of}


def _stoichiometric_species_refs(reaction) -> set[str]:
    """Reactant and product species only (modifiers are ignored for classification)."""
    ids: set[str] = set()
    for collection in (
        reaction.getListOfReactants(),
        reaction.getListOfProducts(),
    ):
        for ref in collection:
            ids.add(ref.getSpecies())
    return ids


def _participant_species_refs(reaction) -> set[str]:
    """All species linked to a reaction: reactants, products, and modifiers."""
    ids = _stoichiometric_species_refs(reaction)
    for ref in reaction.getListOfModifiers():
        ids.add(ref.getSpecies())
    return ids


def _math_symbol_names(node) -> set[str]:
    names: set[str] = set()
    if node is None:
        return names
    if node.isName() or node.isName():
        name = node.getName()
        if name:
            names.add(name)
    for i in range(node.getNumChildren()):
        names |= _math_symbol_names(node.getChild(i))
    return names


def load_species_solvers(species_tsv: str | Path) -> dict[str, str]:
    species_df = pd.read_csv(species_tsv, sep="\t")
    if "speciesId" not in species_df.columns or "solver" not in species_df.columns:
        raise ValueError(f"{species_tsv} must contain speciesId and solver columns")
    return {
        row["speciesId"]: str(row["solver"]).strip().lower()
        for _, row in species_df.iterrows()
    }


def split_species_by_solver(species_solvers: dict[str, str]) -> tuple[set[str], set[str]]:
    """Return (stochastic_species_ids, deterministic_species_ids) from solver labels."""
    stochastic = {sid for sid, solver in species_solvers.items() if solver == "stochastic"}
    deterministic = {sid for sid, solver in species_solvers.items() if solver == "deterministic"}
    return stochastic, deterministic


def classify_reactions(
    model,
    stochastic_species_ids: set[str],
) -> tuple[set[str], set[str]]:
    """
    A reaction is stochastic if any reactant or product is labeled stochastic.
    Modifier-only links to stochastic species do not count.
    All remaining reactions are deterministic.
    """
    stochastic = {
        rxn.getId()
        for rxn in model.getListOfReactions()
        if _stoichiometric_species_refs(rxn) & stochastic_species_ids
    }
    deterministic = _ids(model.getListOfReactions()) - stochastic
    return stochastic, deterministic


def participants_for_reactions(
    model,
    reaction_ids: set[str],
) -> tuple[set[str], set[str]]:
    """
    Species and global parameters that participate in the given reactions.

    Species: reactants, products, modifiers, and symbols in kinetic laws.
    Parameters: global parameter symbols referenced in kinetic laws.
    """
    all_species = _ids(model.getListOfSpecies())
    all_parameters = _ids(model.getListOfParameters())

    species: set[str] = set()
    parameters: set[str] = set()

    for rxn in model.getListOfReactions():
        if rxn.getId() not in reaction_ids:
            continue

        species |= _participant_species_refs(rxn)

        kinetic_law = rxn.getKineticLaw()
        if kinetic_law is None:
            continue

        symbols = _math_symbol_names(kinetic_law.getMath())
        species |= symbols & all_species
        parameters |= symbols & all_parameters

    return species, parameters


def make_empty_model(template_model, model_id: str):
    doc = libsbml.SBMLDocument(template_model.getLevel(), template_model.getVersion())
    new_model = doc.createModel()
    sid = sanitize_model_id(model_id)
    if sid != model_id:
        logger.warning("Sanitized model id %r → %r (SBML SId rules)", model_id, sid)
    new_model.setId(sid)
    if template_model.isSetName():
        new_model.setName(template_model.getName())
    return doc, new_model


def copy_shared_definitions(src, dst) -> None:
    for obj in src.getListOfCompartments():
        dst.addCompartment(obj.clone())
    for obj in src.getListOfFunctionDefinitions():
        dst.addFunctionDefinition(obj.clone())
    for obj in src.getListOfUnitDefinitions():
        dst.addUnitDefinition(obj.clone())


def copy_parameters(src, dst, parameter_ids: set[str]) -> None:
    for parameter in src.getListOfParameters():
        if parameter.getId() in parameter_ids:
            dst.addParameter(parameter.clone())


def copy_species(src, dst, species_ids: set[str]) -> None:
    for species in src.getListOfSpecies():
        if species.getId() in species_ids:
            dst.addSpecies(species.clone())


def copy_reactions(src, dst, reaction_ids: set[str]) -> None:
    for reaction in src.getListOfReactions():
        if reaction.getId() in reaction_ids:
            dst.addReaction(reaction.clone())


def _build_reduced_partition(
    src_model,
    model_id: str,
    reaction_ids: set[str],
):
    species_ids, parameter_ids = participants_for_reactions(src_model, reaction_ids)

    doc, dst = make_empty_model(src_model, model_id)
    copy_shared_definitions(src_model, dst)
    copy_parameters(src_model, dst, parameter_ids)
    copy_species(src_model, dst, species_ids)
    copy_reactions(src_model, dst, reaction_ids)
    return doc, species_ids, parameter_ids


def partition_sbml(
    sbml_path: str | Path,
    species_tsv: str | Path,
    output_dir: str | Path,
    *,
    stochastic_model_id: str = "stochastic-gene-expression",
    deterministic_model_id: str = "deterministic-interactions",
) -> PartitionResult:
    """Split ``sbml_path`` into reduced stochastic and deterministic SBML files."""
    sbml_path = Path(sbml_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reader = libsbml.SBMLReader()
    doc = reader.readSBML(str(sbml_path))
    model = doc.getModel()
    if model is None:
        raise RuntimeError(f"Could not parse SBML model from {sbml_path}")

    species_solvers = load_species_solvers(species_tsv)
    stochastic_labeled, _ = split_species_by_solver(species_solvers)
    stochastic_rxns, deterministic_rxns = classify_reactions(model, stochastic_labeled)

    stoch_doc, stoch_species, stoch_params = _build_reduced_partition(
        model, stochastic_model_id, stochastic_rxns
    )
    det_doc, det_species, det_params = _build_reduced_partition(
        model, deterministic_model_id, deterministic_rxns
    )

    writer = libsbml.SBMLWriter()
    # Keep filenames as requested (may contain hyphens); model @id is sanitized.
    stoch_path = output_dir / f"{stochastic_model_id}.xml"
    det_path = output_dir / f"{deterministic_model_id}.xml"
    writer.writeSBML(stoch_doc, str(stoch_path))
    writer.writeSBML(det_doc, str(det_path))

    logger.info(
        "Partitioned %s → %s (%d rxns, %d species, %d params) and "
        "%s (%d rxns, %d species, %d params)",
        sbml_path.name,
        stoch_path.name,
        len(stochastic_rxns),
        len(stoch_species),
        len(stoch_params),
        det_path.name,
        len(deterministic_rxns),
        len(det_species),
        len(det_params),
    )

    return PartitionResult(
        stochastic_path=stoch_path,
        deterministic_path=det_path,
        stochastic_reaction_ids=stochastic_rxns,
        deterministic_reaction_ids=deterministic_rxns,
        stochastic_species_ids=stoch_species,
        deterministic_species_ids=det_species,
        stochastic_parameter_ids=stoch_params,
        deterministic_parameter_ids=det_params,
    )


def _compare_sets(label: str, expected: set[str], actual: set[str], messages: list[str]) -> None:
    missing = expected - actual
    extra = actual - expected
    if missing:
        messages.append(f"{label}: missing {len(missing)} ids (e.g. {sorted(missing)[:5]})")
    if extra:
        messages.append(f"{label}: unexpected extra {len(extra)} ids (e.g. {sorted(extra)[:5]})")


def verify_partition(
    one4all_path: str | Path,
    stochastic_path: str | Path,
    deterministic_path: str | Path,
    *,
    stochastic_reaction_ids: set[str] | None = None,
    deterministic_reaction_ids: set[str] | None = None,
    species_tsv: str | Path | None = None,
) -> VerificationReport:
    """
    Confirm partitioned models form a reduced, reaction-disjoint cover.

    Checks:
      - reaction IDs form a disjoint cover of the One4All reactions
      - each partition's species/parameters exactly match reaction participants
      - compartments / function definitions / unit definitions are shared in full
      - translation ``vTL*`` is deterministic; ``vTC*`` / ``vTCd*`` / ``vGac*`` /
        ``vGin*`` for stochastic-labeled genes are stochastic (when species_tsv given)
    """
    reader = libsbml.SBMLReader()
    messages: list[str] = []

    def load(path: Path):
        model = reader.readSBML(str(path)).getModel()
        if model is None:
            raise RuntimeError(f"Could not parse SBML model from {path}")
        return model

    full = load(Path(one4all_path))
    stoch = load(Path(stochastic_path))
    det = load(Path(deterministic_path))

    full_rxns = _ids(full.getListOfReactions())
    stoch_rxns = _ids(stoch.getListOfReactions())
    det_rxns = _ids(det.getListOfReactions())

    if stochastic_reaction_ids is not None:
        _compare_sets("stochastic reactions (vs classifier)", stochastic_reaction_ids, stoch_rxns, messages)
    if deterministic_reaction_ids is not None:
        _compare_sets("deterministic reactions (vs classifier)", deterministic_reaction_ids, det_rxns, messages)

    overlap = stoch_rxns & det_rxns
    if overlap:
        messages.append(f"reactions appear in both partitions: {sorted(overlap)[:5]}")

    _compare_sets("reaction cover vs One4All", full_rxns, stoch_rxns | det_rxns, messages)

    for label, child, rxn_ids in (
        ("stochastic", stoch, stoch_rxns),
        ("deterministic", det, det_rxns),
    ):
        expected_species, expected_params = participants_for_reactions(full, rxn_ids)
        _compare_sets(f"{label} species (participants)", expected_species, _ids(child.getListOfSpecies()), messages)
        _compare_sets(
            f"{label} parameters (participants)",
            expected_params,
            _ids(child.getListOfParameters()),
            messages,
        )

        unknown_species = _ids(child.getListOfSpecies()) - _ids(full.getListOfSpecies())
        if unknown_species:
            messages.append(f"{label} species not in One4All: {sorted(unknown_species)[:5]}")

        unknown_params = _ids(child.getListOfParameters()) - _ids(full.getListOfParameters())
        if unknown_params:
            messages.append(f"{label} parameters not in One4All: {sorted(unknown_params)[:5]}")

    # Shared non-parameter globals remain complete in both children.
    for label, child in (("stochastic", stoch), ("deterministic", det)):
        for kind, getter in (
            ("compartments", lambda m: m.getListOfCompartments()),
            ("functionDefinitions", lambda m: m.getListOfFunctionDefinitions()),
            ("unitDefinitions", lambda m: m.getListOfUnitDefinitions()),
        ):
            _compare_sets(
                f"{label} {kind}",
                _ids(getter(full)),
                _ids(getter(child)),
                messages,
            )

    # Reaction-family placement checks.
    vtl_in_stoch = {r for r in stoch_rxns if r.startswith("vTL")}
    if vtl_in_stoch:
        messages.append(
            f"translation reactions in stochastic partition: {sorted(vtl_in_stoch)[:5]}"
        )

    if species_tsv is not None:
        stochastic_labeled, _ = split_species_by_solver(load_species_solvers(species_tsv))
        gene_rxn_prefixes = ("vTC", "vTCd", "vGac", "vGin")
        for rid in det_rxns:
            if not rid.startswith(gene_rxn_prefixes):
                continue
            rxn = full.getReaction(rid)
            if rxn is None:
                continue
            stoich = _stoichiometric_species_refs(rxn)
            if stoich & stochastic_labeled:
                messages.append(
                    f"stochastic-gene reaction {rid} assigned to deterministic partition"
                )

    # Apoptosis proteins must not appear as species in the stochastic partition.
    apoptosis_markers = ("cl_PARP", "cl_CASP3", "cyt_prot__XIAP")
    stoch_spp = _ids(stoch.getListOfSpecies())
    for marker in apoptosis_markers:
        hits = sorted(s for s in stoch_spp if marker in s)
        if hits:
            messages.append(f"apoptosis species in stochastic partition: {hits[:5]}")

    ok = not messages
    if ok:
        messages.append(
            "OK: reactions form a disjoint cover; each partition retains only "
            "participant species/parameters for its reactions; translation is "
            "deterministic and apoptosis proteins are det-only."
        )
        logger.info(messages[-1])
    else:
        for msg in messages:
            logger.error(msg)

    return VerificationReport(ok=ok, messages=messages)
