# Theory

This page collects the equations and the methodological assumptions
behind `swmm-breach` in one place. Full citations are in the
[changelog and references](changelog.md) and in the manuscript
References section at `paper/jwmm/manuscript.md`.

## Breach parameter regressions

### Froehlich (2008)

Fit to a database of 74 historical embankment-dam failures. Predicts the
average breach bottom width and the formation time as:

$$B_{avg} = 0.27 \, K_o \, V_w^{0.32} \, h_b^{0.04}$$

$$t_f = 63.2 \sqrt{\frac{V_w}{g \, h_b^2}}$$

with $K_o = 1.3$ for overtopping failures, $K_o = 1.0$ for piping;
$V_w$ in m³, $h_b$ in m, $B_{avg}$ in m, $t_f$ in seconds,
$g = 9.80665$ m/s².

Side slopes: $1.0$ (H:V) for overtopping, $0.7$ for piping.

### Froehlich (1995)

The predecessor regression, fit to 63 cases with different exponents:

$$B_{avg} = 0.1803 \, K_o \, V_w^{0.32} \, h_b^{0.19}$$

$$t_f = 0.00254 \, V_w^{0.53} \, h_b^{-0.90}$$

with $K_o = 1.4$ for overtopping, $K_o = 1.0$ for piping; $t_f$ in
hours. Side slope $0.9$ across modes.

Including both regressions enables sampling across **model uncertainty**
(which generation of the regression is appropriate) in addition to the
within-model **parameter uncertainty** captured by Monte Carlo residual
sampling.

## Outflow hydraulics

Outflow through the developing trapezoidal breach is computed as a
broad-crested weir with rectangular and triangular components:

$$Q = C_w \, B \, h^{1.5} + \frac{8}{15} \, C_w \, z \, h^{2.5}$$

where:

- $C_w = 1.7$ m$^{0.5}$/s is the broad-crested weir coefficient (SI)
- $B$ is the current bottom width (metres)
- $z$ is the side slope (H per V)
- $h$ is the current head from the upstream water surface to the breach invert (metres)

## Breach growth model

The breach is assumed to grow linearly from zero bottom width and zero
vertical extent to its fully-developed $B_{avg}$ and $h_b$ over the
formation time $t_f$. This is the simplest possible representation and
the standard engineering simplification for empirical breach forecasting.

**Limitation:** real breaches go through phases (initial overtopping or
piping, headcut formation, vertical erosion, lateral widening) that do
not develop linearly. The linear-growth assumption tends to overestimate
peak outflow at large-dam scales where headcut migration is a first-
order process.

## Reservoir routing

Mass balance is integrated explicitly:

$$\frac{dV}{dt} = I - Q$$

where $V$ is the reservoir volume, $I$ is any external inflow (zero by
default), and $Q$ is the breach outflow computed above. The water
surface elevation is recovered at each step from the inverse of the
stage-storage curve via linear interpolation.

## Wahl (2004) Monte Carlo uncertainty propagation

For each Monte Carlo realization, the breach width $B_{avg}$ and
formation time $t_f$ are drawn from log-normal residual distributions
centered on the regression's central estimate:

$$B_{avg,i} = B_{avg,central} \cdot 10^{Z_{B,i}}, \quad Z_{B,i} \sim \mathcal{N}(0, \sigma_{\log B_{avg}}^2)$$

$$t_{f,i} = t_{f,central} \cdot 10^{Z_{t,i}}, \quad Z_{t,i} \sim \mathcal{N}(0, \sigma_{\log t_f}^2)$$

The default residual standard deviations for Froehlich (2008) are
$\sigma_{\log B_{avg}} = 0.110$ and $\sigma_{\log t_f} = 0.197$,
consistent with the residual statistics reported in Froehlich's
paper. For Froehlich (1995) the defaults are
$\sigma_{\log B_{avg}} = 0.137$ and $\sigma_{\log t_f} = 0.220$,
reflecting the larger residuals of the older regression's smaller
fitted dataset.

These defaults can be overridden for project-specific calibration:

```python
from swmm_breach.uncertainty import FroehlichUncertainty
custom = FroehlichUncertainty(sigma_log_b_avg=0.15, sigma_log_t_f=0.25)
```

## Multi-model ensemble

For multi-model sampling, each realization independently selects one
model from a user-supplied set according to its weight:

$$\text{Model}_i \sim \text{Categorical}(w_1, \dots, w_M)$$

then samples $B_{avg}$ and $t_f$ from that model's residual
distribution. The default two-model ensemble uses Froehlich (2008) and
Froehlich (1995) with equal weight; the `BreachModel` interface accepts
arbitrary user-defined models.

The result captures both:

- **Parametric uncertainty** (within-model residual sampling) — Wahl 2004's recommendation
- **Epistemic uncertainty** (which regression family is appropriate) — extension to multi-model

## References

- Froehlich, D. C. (1995). Embankment Dam Breach Parameters Revisited. ASCE Water Resources Engineering Proceedings.
- Froehlich, D. C. (2008). Embankment Dam Breach Parameters and Their Uncertainties. *J. Hydraul. Eng.* 134(12), 1708-1721.
- Rossman, L. A. (2017). Storm Water Management Model Reference Manual. EPA/600/R-17/111.
- Wahl, T. L. (2004). Uncertainty of Predictions of Embankment Dam Breach Parameters. *J. Hydraul. Eng.* 130(5), 389-397.
