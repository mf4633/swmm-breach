"""Generate per-tutorial ensemble envelope figures.

Run from the package root after installing the docs/viz extras:

    pip install -e ".[docs]"
    python docs/generate_tutorial_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from swmm_breach import FailureMode, StorageCurve
from swmm_breach.uncertainty import ensemble_simulate_multi_model

OUT = Path(__file__).parent / "figures"


def _save_envelope(ens, observed_low, observed_high, title, fname, x_max_min):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ens.plot_envelope(
        ax=ax, low_pct=5.0, high_pct=95.0,
        show_realizations=True, n_realizations=20,
        rng=np.random.default_rng(0),
    )
    ax.axhspan(observed_low, observed_high, color="firebrick", alpha=0.18,
               label="reference peak")
    ax.set_xlim(0, x_max_min)
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=150)
    plt.close(fig)
    print(f"wrote {OUT / fname}")


def anson_figure():
    NP = 458.89 * 0.3048
    CR = 463.5 * 0.3048
    TOE = CR - 25.0 * 0.3048
    sc = StorageCurve(
        stage_m=np.array([TOE, 136.5, NP, CR]),
        volume_m3=np.array([0, 10_000, 64.0 * 1233.48, 111 * 1233.48]),
    )
    ens = ensemble_simulate_multi_model(
        storage=sc, crest_elevation_m=NP, initial_stage_m=NP,
        volume_m3=64.0 * 1233.48, height_m=NP - TOE,
        mode=FailureMode.PIPING,
        n_samples=2000, dt_s=2.0, duration_s=2 * 3600,
        rng=np.random.default_rng(20260511),
    )
    _save_envelope(
        ens,
        observed_low=121.8, observed_high=121.8,
        title="Anson Lower Lagoon (2026) -- piping at NP, n=2000",
        fname="anson_ensemble.png",
        x_max_min=120,
    )


def lawn_lake_figure():
    sc = StorageCurve(
        stage_m=np.array([0.0, 1.5, 3.0, 4.5, 6.4]),
        volume_m3=np.array([0, 90_000, 250_000, 470_000, 798_500]),
    )
    ens = ensemble_simulate_multi_model(
        storage=sc, crest_elevation_m=6.4, initial_stage_m=6.4,
        volume_m3=798_500, height_m=6.4,
        mode=FailureMode.PIPING,
        n_samples=2000, dt_s=2.0, duration_s=3 * 3600,
        rng=np.random.default_rng(20260511),
    )
    _save_envelope(
        ens,
        observed_low=510.0, observed_high=510.0,
        title="Lawn Lake Dam (1982) -- piping at full pool, n=2000",
        fname="lawn_lake_ensemble.png",
        x_max_min=180,
    )


def teton_figure():
    sc = StorageCurve(
        stage_m=np.array([0.0, 20.0, 40.0, 60.0, 80.0, 87.0]),
        volume_m3=np.array([0.0, 12e6, 60e6, 160e6, 290e6, 308e6]),
    )
    ens = ensemble_simulate_multi_model(
        storage=sc, crest_elevation_m=87.0, initial_stage_m=87.0,
        volume_m3=308e6, height_m=86.9,
        mode=FailureMode.PIPING,
        n_samples=2000, dt_s=15.0, duration_s=4 * 3600,
        rng=np.random.default_rng(20260511),
    )
    _save_envelope(
        ens,
        observed_low=50_000.0, observed_high=80_000.0,
        title="Teton Dam (1976) -- piping at NP, n=2000",
        fname="teton_ensemble.png",
        x_max_min=240,
    )


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    anson_figure()
    lawn_lake_figure()
    teton_figure()
