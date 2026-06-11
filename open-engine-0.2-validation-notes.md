# Open 0.2 Engine Validation Ties (for JWMM / deterministic breach contrast)

This document ties swmm-breach work to the new open-core 0.2 hydrology engine (verified across implementations).

## Verified 0.2 Primitives (same in py/js/rust/wasm)
- manning_full_flow_circular ~15.996
- manning_normal_flow_trapezoidal ~17.656
- manning_friction_head_loss (HGL hglStep0_2) ~0.500
- simple_linear_reservoir_routing ~6.321
- critical_depth_circular ~0.658
- normal_depth_circular ~1.000
- energy_grade_line_step (EGL) ~0.500

See:
- hydro-tools/rational.py
- dev/OpenCADStudio/crates/stormsewer (Rust/WASM)
- hc-refactored/src/calc (JS)
- pe-calc / FieldHydro pro (AR/batch)

"never gate fundamentals" • "core free, pro on top (FieldHydro/HydroComplete)"

## Relation to swmm-breach
- Provides modern, auditable, multi-RP, LandXML/SSN-based network analysis as contrast to deterministic single-storm breach modeling.
- Enables probabilistic workflows, full HEC-22 style inlets (future), and provenance exports.
- Dispatch package for pilots: real-dispatch-package-5-leads/REAL_DISPATCH_PACKAGE.md (EXECUTION_READY)
- Feedback: .github/ISSUE_TEMPLATE/engine-feedback.md

## Next
Expand swmm-breach runnable examples to call 0.2 primitives for hybrid validation.

(Added as part of Phase 3 open-core work, June 2026)
