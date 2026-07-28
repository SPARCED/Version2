#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mpi4py import MPI


def now():
    return MPI.Wtime()

