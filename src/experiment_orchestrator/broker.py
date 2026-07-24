#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mpi4py import MPI

from config.settings import BROKER_RANK


def broker(comm, rank, size, config):
    print("Hello from the broker!")

