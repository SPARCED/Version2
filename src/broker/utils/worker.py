#!/usr/bin/env python
# -*- coding: utf-8 -*-


def compute_assigned_cell_ids(nb_cells: int, worker_rank: int, size: int) -> list[int]:
    nb_workers = size - 1   # Discard broker
    return [cell for cell in range(worker_rank, nb_cells+1, nb_workers)]

