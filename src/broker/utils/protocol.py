#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any

from config.protocol_file_format import ProtocolContextKeys

from broker.simulation_step import SimulationStep


def load_protocol(context: dict[str, Any]) -> list[SimulationStep]:
    protocol = []

    for s in context[ProtocolContextKeys.PROTOCOL_DETAILS]:
        step = SimulationStep(s, context[ProtocolContextKeys.PROTOCOL_NAME])
        protocol.append(step)

    return protocol

