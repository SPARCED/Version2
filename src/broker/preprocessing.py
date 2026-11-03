#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from config.paths import PROTOCOLS_DIR_PATH

from validators.protocol import ProtocolValidator


def load_protocol(protocol_relative_path: str | Path):
    protocol_path = PROTOCOLS_DIR_PATH / Path(protocol_relative_path.lstrip("/\\"))

    protocol = ProtocolValidator.load_valid(protocol_path)

    return protocol

