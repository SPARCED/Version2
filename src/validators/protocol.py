#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any

import yaml

from config.protocol_file_format import EXTENSION as PROTOCOL_SUFFIX

from validators.path import PathValidator


class ProtocolValidator:
    @classmethod
    def load_valid(path: str | Path) -> dict[str, Any]:
        protocol = cls._load(path)
        
        cls._validate_structure(protocol)
        cls._validate_content(protocol)

        return protocol

    @staticmethod
    def _load(path: str | Path) -> dict[str, Any]:
        path = PathValidator.file(path, PROTOCOL_SUFFIX)

        with path.open("r", encoding="utf-8") as f:
            protocol = yaml.safe_load(f)

        return protocol

    @staticmethod
    def _validate_structure(protocol: dict[str, Any]) -> None:
        if not isinstance(protocol, dict):
            raise ValueError("Protocol is not a dictionnary")

    @staticmethod
    def _validate_content(protocol: dict[str, Any]) -> None:
        pass

