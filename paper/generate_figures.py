"""Regenerate figures embedded in paper.md.

Run from the package root after installing the viz extra:

    python -m pip install -e ".[viz]"
    python paper/generate_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from swmm_breach import FailureMode, StorageCurve
from swmm_breach.uncertainty import ensemble_simulate_multi_model

OUT_DIR = Path(__file__).parent
TETON_OBSERVED_LOW = 50_000.0
TETON_OBSERVED_HIGH = 80_000.0


def teton_ensemble_figure() -> None:
    storage = StorageCurve(
        stage_m=np.array([0.0, 20.0, 40.0, 60.0, 80.0, 87.0]),
        volume_m3=np.array([0.0, 12e6, 60e6, 160e6, 290e6, 308e6]),
    )
    ens = ensemble_simulate_multi_model(
        storage=storage,
        crest_elevation_m=87.0,
        initial_stage_m=87.0,
        volume_m3=308e6,
        height_m=86.9,
        mode=FailureMode.PIPING,
        n_samples=2000,
        dt_s=15.0,
        duration_s=4 * 3600,
        rng=np.random.default_rng(20260511),
    )

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ens.plot_envelope(
        ax=ax,
        low_pct=5.0,
        high_pct=95.0,
        show_realizations=True,
        n_realizations=30,
        rng=np.random.default_rng(0),
    )
    # Overlay the historically reported peak band
    ax.axhspan(
        TETON_OBSERVED_LOW, TETON_OBSERVED_HIGH,
        color="firebrick", alpha=0.18,
        label="Teton observed peak (50,000-80,000 m$^3$/s)",
    )
    ax.set_xlim(0, 240)
    ax.set_title("Teton Dam (1976) -- multi-model ensemble (n=2000)")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    out = OUT_DIR / "teton_ensemble.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")
    plt.close(fig)


if __name__ == "__main__":
    teton_ensemble_figure()
