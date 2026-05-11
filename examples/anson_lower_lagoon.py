"""Anson County WTP Lower Lagoon Dam (ANSON-057) -- swmm-breach vs HEC-RAS.

This case study reproduces a real PE engagement: a piping breach of the
Lower Lagoon at normal pool, originally analyzed in HEC-RAS 6.6 (2D
unsteady) as part of a Class C to Class A hazard reclassification
submittal to the NC Dam Safety Program.

Embankment parameters (NAVD88, from the as-built 2023 survey and the
Anson County WTP Sludge Lagoon Dams O&M Plan, May 2026):

    Structural height    25 ft  (7.62 m)
    Crest elevation      463.5 ft (NAVD88)
    Normal pool          458.89 ft
    Volume at NP         64.0 ac-ft  (78,940 m^3)
    Volume at crest      111 ac-ft   (~136,930 m^3)
    Failure mode         piping (HDPE-lined embankment, no chimney drain)

HEC-RAS result for the Lower-piping-at-NP scenario: peak breach
outflow Q = 4,301 cfs (121.8 m^3/s).
"""

import numpy as np

from swmm_breach import FailureMode, StorageCurve, froehlich, simulate
from swmm_breach.uncertainty import ensemble_simulate


# ---- Embankment parameters ----------------------------------------------
NP_ELEV_M = 458.89 * 0.3048              # 139.87 m
CREST_ELEV_M = 463.5 * 0.3048            # 141.27 m
STRUCTURAL_HEIGHT_M = 25.0 * 0.3048      # 7.62 m
TOE_ELEV_M = CREST_ELEV_M - STRUCTURAL_HEIGHT_M  # 133.65 m

VOL_NP_M3 = 64.0 * 1233.48     # ac-ft -> m^3 = 78,943
VOL_CREST_M3 = 111.0 * 1233.48                   # 136,916

# Approximate lagoon stage-storage (lined basin geometry; volume below
# NP scales roughly with the inverted truncated cone of the embankment).
storage = StorageCurve(
    stage_m=np.array([TOE_ELEV_M, 136.5, NP_ELEV_M, CREST_ELEV_M]),
    volume_m3=np.array([0.0, 10_000.0, VOL_NP_M3, VOL_CREST_M3]),
)

BREACH_HEIGHT_M = NP_ELEV_M - TOE_ELEV_M  # 6.22 m

HEC_RAS_PEAK_M3S = 4301.0 / 35.31466621  # 121.8 m^3/s


def main() -> None:
    # ---- Deterministic Froehlich + level-pool ----
    geom = froehlich.predict(
        volume_m3=VOL_NP_M3,
        height_m=BREACH_HEIGHT_M,
        crest_elevation_m=NP_ELEV_M,  # piping at NP, breach develops from NP downward
        mode=FailureMode.PIPING,
    )
    hg = simulate(
        geometry=geom,
        storage=storage,
        crest_elevation_m=NP_ELEV_M,
        initial_stage_m=NP_ELEV_M,
        dt_s=2.0,
        duration_s=2 * 3600,
    )

    # ---- Monte Carlo ensemble (Wahl 2004 style) ----
    ens = ensemble_simulate(
        storage=storage,
        crest_elevation_m=NP_ELEV_M,
        initial_stage_m=NP_ELEV_M,
        volume_m3=VOL_NP_M3,
        height_m=BREACH_HEIGHT_M,
        mode=FailureMode.PIPING,
        n_samples=2000,
        dt_s=2.0,
        duration_s=2 * 3600,
        rng=np.random.default_rng(20260511),
    )

    print("=== Anson Lower Lagoon (ANSON-057) -- piping at NP ===")
    print(f"Reservoir volume at NP : {VOL_NP_M3:,.0f} m^3 (64.0 ac-ft)")
    print(f"Breach height          : {BREACH_HEIGHT_M:.2f} m (NP - structural toe)")
    print()
    print("Froehlich (2008) point estimate:")
    print(f"  B_avg                : {geom.bottom_width_m:.1f} m")
    print(f"  t_f                  : {geom.formation_time_s/60:.1f} min")
    print()
    print("Deterministic level-pool routing:")
    print(f"  Peak Q               : {hg.peak_outflow_m3s:.1f} m^3/s "
          f"({hg.peak_outflow_m3s * 35.31466621:.0f} cfs)")
    print(f"  Time to peak         : {hg.time_to_peak_s/60:.1f} min")
    print()
    print("Probabilistic ensemble (n=2000):")
    print(f"  Peak Q  5/50/95%     : {ens.peak_percentile(5):.1f} / "
          f"{ens.peak_percentile(50):.1f} / {ens.peak_percentile(95):.1f} m^3/s")
    print(f"                       : {ens.peak_percentile(5)*35.314:.0f} / "
          f"{ens.peak_percentile(50)*35.314:.0f} / "
          f"{ens.peak_percentile(95)*35.314:.0f} cfs")
    print()
    print("Reference (HEC-RAS 6.6 2D unsteady):")
    print(f"  Peak Q               : {HEC_RAS_PEAK_M3S:.1f} m^3/s "
          f"(4,301 cfs)")
    print()
    p5, p95 = ens.peak_percentile(5), ens.peak_percentile(95)
    if p5 <= HEC_RAS_PEAK_M3S <= p95:
        print(f"==> HEC-RAS peak lies within ensemble 5-95 envelope: "
              f"[{p5:.0f}, {p95:.0f}] m^3/s")
    else:
        print(f"==> HEC-RAS peak {HEC_RAS_PEAK_M3S:.0f} m^3/s lies OUTSIDE "
              f"ensemble [{p5:.0f}, {p95:.0f}] m^3/s")


if __name__ == "__main__":
    main()
