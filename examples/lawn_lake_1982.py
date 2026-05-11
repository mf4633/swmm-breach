"""Lawn Lake Dam (1982) -- third historical validation case.

Lawn Lake (Rocky Mountain National Park, Colorado) failed by piping on
15 July 1982.  The reservoir parameters and observed peak discharge are
from the public USGS report Jarrett & Costa (1986).
"""

import numpy as np

from swmm_breach import FailureMode, StorageCurve
from swmm_breach.uncertainty import ensemble_simulate_multi_model

VOL_M3 = 798_500.0
H_B_M = 6.4
OBS_PEAK_M3S = 510.0


def main() -> None:
    sc = StorageCurve(
        stage_m=np.array([0.0, 1.5, 3.0, 4.5, 6.4]),
        volume_m3=np.array([0.0, 90_000, 250_000, 470_000, 798_500]),
    )
    ens = ensemble_simulate_multi_model(
        storage=sc,
        crest_elevation_m=H_B_M,
        initial_stage_m=H_B_M,
        volume_m3=VOL_M3,
        height_m=H_B_M,
        mode=FailureMode.PIPING,
        n_samples=2000,
        dt_s=2.0,
        duration_s=3 * 3600,
        rng=np.random.default_rng(20260511),
    )
    print("=== Lawn Lake Dam (1982) -- piping at full pool ===")
    print(f"Reservoir volume     : {VOL_M3:,.0f} m^3")
    print(f"Breach height        : {H_B_M:.2f} m")
    print()
    print("Multi-model ensemble (Froehlich 2008 + Froehlich 1995, n=2000):")
    print(f"  Peak Q  5/50/95%   : {ens.peak_percentile(5):.1f} / "
          f"{ens.peak_percentile(50):.1f} / {ens.peak_percentile(95):.1f} m^3/s")
    print()
    print(f"Observed (Jarrett & Costa 1986):  {OBS_PEAK_M3S:.0f} m^3/s")
    p5, p95 = ens.peak_percentile(5), ens.peak_percentile(95)
    if p5 <= OBS_PEAK_M3S <= p95:
        print(f"==> Observed lies within 5-95 envelope [{p5:.0f}, {p95:.0f}] m^3/s")
    else:
        print(f"==> Observed OUTSIDE envelope [{p5:.0f}, {p95:.0f}] m^3/s")


if __name__ == "__main__":
    main()
