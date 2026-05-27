"""swmm-breach: dam breach hydrograph generator for EPA SWMM and PCSWMM."""

from .breach import BreachGeometry, FailureMode
from . import froehlich, froehlich_1995, output, swmm, uncertainty
from .reservoir import StorageCurve, trapezoidal_breach_outflow
from .hydrograph import Hydrograph, simulate

__version__ = "0.8.0"

__all__ = [
    "BreachGeometry",
    "FailureMode",
    "froehlich",
    "froehlich_1995",
    "output",
    "swmm",
    "uncertainty",
    "StorageCurve",
    "Hydrograph",
    "simulate",
    "trapezoidal_breach_outflow",
]
