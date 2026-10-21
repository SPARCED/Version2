# Abstract base class for simulator wrappers (Tellurium, AMICI, etc.).
# This file originates from Benchtop (f25d654)
# Written by Jonah R. Huggins

from abc import ABC, abstractmethod
from types import ModuleType


class AbstractSolver(ABC):
    """Interface: load model, modify state, simulate over a time grid."""

    def __init__(self, *args, **kwargs):
        self.tool = type("Tool", (), {})()
        self.load(*args, **kwargs)

    @abstractmethod
    def load(self, *args, **kwargs) -> ModuleType:
        """Load or compile the model from constructor arguments."""

    @abstractmethod
    def modify(self, component: str, value: float) -> None:
        """Set a parameter or species value before simulation."""

    @abstractmethod
    def simulate(self, start: float, stop: float, step: float):
        """Integrate from start to stop with given step; return trajectory."""
