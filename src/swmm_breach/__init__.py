"""swmm-breach: dam breach hydrograph generator for EPA SWMM and PCSWMM."""

from .breach import BreachGeometry, FailureMode
from . import froehlich
from .reservoir import StorageCurve, trapezoidal_breach_outflow
from .hydrograph import Hydrograph, simulate

__version__ = "0.1.0"

__all__ = [
    "BreachGeometry",
    "FailureMode",
    "froehlich",
    "StorageCurve",
    "Hydrograph",
    "simulate",
    "trapezoidal_breach_outflow",
]
