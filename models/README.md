# Models -- draft documentation

Models in the _workspace_ folder are ignored by Git.

## List of available official models

    - 2022: SPARCED, as published in _Nat. comm._
    - 2023: SPARCED, as published in _Bioinformatics Advances_ **(ongoing)**
    - 2025: SPARCED, as published in _PLOS Comput. Biol._
    - 2027: SingleCell, expanded with drugs
    - SingleCell: SingleCell, as in Jonah's repository
    - drugs: individual submodels for several anticancer drugs
    - stochastic-gene-expression-v1.4.2: SPARCED v 1.4.2, as provided by Jonah

## Input data files structure

### Compartments

| ----------- | -------- | ---------- | ------- |
| compartment | volume   | annotation | fieldId |
| name: str   | L: float | GO: str    | str     |
| ----------- | -------- | ---------- | ------- |

### Parameters

| ---------- | ------------ | -------------- | ---------- | ---------- | ------------ | -------- |
| reactionId | parameterId  | parameterScale | lowerBound | upperBound | nominalValue | estimate |
| str        | reaction\_nb | lin            | Three identical values                 | 0        |
| -----------| ------------ | -------------- | ------------------------------------------------- |

### Ratelaws

| ---------- | ----------- | ------------------------------------- | ------- |
| reactionId | compartment | equation                              | formula |
| str        | str         | SBMLUtils compatible str + [modifier] | str     |
| ---------- | ----------- | ------------------------------------- | ------- |

### Species

| --------- | ----------- | ---- | -------------------- | --------------------------- | ------------------- |
| speciesId | compartment | type | initialConcentration | solver                      | annotation          |
| name: str | str         | str  | nM: float            | Deterministic or Stochastic | comma-separated str |
| --------- | ----------- | ---- | -------------------- | --------------------------- | ------------------- |

