#!/usr/bin/env python
# -*- coding: utf-8 -*-

from broker.run import run_experiment

if __name__ == "__main__":
    run_experiment("official/benchmarks/cell_cycle.yml", "DEBUG")

