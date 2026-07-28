#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


def setup(level: str = "INFO", rank: int | None = None) -> None:
    prefix = ""

    if rank is not None:
        prefix = f"[R{rank:03d}]"

    logging.basicConfig(
            level = getattr(logging, level.upper()),
            format = f"{prefix} [%(levelname)-8s] %(message)s"
            )

log = logging.getLogger(__name__)

