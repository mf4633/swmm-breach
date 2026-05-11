"""swmm-breach: dam breach hydrograph generator for EPA SWMM and PCSWMM."""

from .breach import BreachGeometry, FailureMode
from . import froehlich, output, swmm, uncertainty
from .reservoir import StorageCurve, trapezoidal_breach_outflow
from .hydrograph import Hydrograph, simulate

__version__ = "0.4.0"

__all__ = [
    "BreachGeometry",
    "FailureMode",
    "froehlich",
    "output",
    "swmm",
    "uncertainty",
    "StorageCurve",
    "Hydrograph",
    "simulate",
    "trapezoidal_breach_outflow",
]
