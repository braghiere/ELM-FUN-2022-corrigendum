# ELM-FUN 2022 corrigendum check

Paired global re-run of the ELM-FUN (FUN-P) simulation behind **Braghiere et al. (2022, JAMES)** to quantify
the effect of two inherited FUN code defects and decide whether a corrigendum is warranted.

## The two defects (both hardcoded in `CNFUNMod.F90`, so paramfile-independent)
- **A. Non-mycorrhizal uptake cost swapped** (CLM5 lineage, [ESCOMP/CTSM #2120](https://github.com/ESCOMP/CTSM/issues/2120)):
  live tier has `kc_nonmyc = 0.15, kn_nonmyc = 0.015` (root-C term large, soil-N term small). Fix: exchange them.
- **B. PFT-index typo**: `ivt(p).eq.7` should be `.eq.17` in the AM active-cost tier, putting PFT 7 (temperate
  broadleaf deciduous) in the C4-grass/corn tier. Fix: one character.
- Also wired (physics-neutral): `npp_Nam/npp_Necm/npp_Pam/npp_Pecm` AM/EcM carbon-flux diagnostics, which are
  declared as history outputs but never assigned in the 2022 source (identically zero in the published files).

## Design
Two chains, identical except the three physics lines (control = 2022 code + diagnostics; corrected = + fix):
f19 (1.9x2.5), GSWP3 v2 cpl_bypass forcing, 260 yr AD spin-up -> 280 yr final spin-up (branch at year 541,
as the published v6 transient did) -> 1850-2010 transient. Tree: `elm_fun_trendy_2022/E3SM_global`
(byte-identical FUN code to the 2022 build), CIME `cades` config ported from the tree that built on CADES
in July 2026. Per-chain code via CIME `SourceMods` (tree physics untouched).

## Layout
- `source/` original 2022 `CNFUNMod.F90` + the three derived versions (md5s in docs/PLAN.md); corrected paramfile
- `patches/` `apply_fun_fix.py` (validated: exactly 1 B-fix + 4 A-swaps), `wire_am_ecm_diag.py`
- `runs/` per-chain SourceMods, OLMT commands, job IDs, logs
- `analysis/` re-plot for the Ashley collaboration (`REPLOT_README.md`) and, later, control-vs-corrected results
- `docs/PLAN.md` step-by-step plan, provenance, status
