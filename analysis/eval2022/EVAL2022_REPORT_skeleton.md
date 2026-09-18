# Redo of the Braghiere et al. (2022) evaluation: archived product vs control rerun vs corrected rerun
(Skeleton written 2026-09-18 evening; the rerun columns are filled by `run_eval.sh 1994-2005` after the transients finish.)

## 0. What is compared
- **published_FUNP**: archived ELM-FUN3.0 product (`fix_global_v6_funp`, = Zenodo 10.5281/zenodo.20452251, bit-identical 1994–2005 means).
- **control**: rerun of the same 2022 code from a fresh 2020-tree FUN-off spin-up (260 + 540 yr), transient 1850–2010 with the 2020 surface
  dataset (c171002) and a CO₂ series that covers 2006–2010.
- **corrected**: identical to control except the three bundled FUN fixes (A larch kc/kn swap, B PFT-7 tier typo [numerically inert],
  C hardcoded fixation-cost override removed) and the AM/EcM cost diagnostics wired.
- published_ELM / published_FUN2: archived baselines for Figs 2–4 (not rerun).

## 1. Findings about the archived product and the paper (independent of the reruns)
1. CO₂ forcing file ends 2007 → all three archived products invalid from mid-2009 (GPP → 0). Paper period 1994–2005 unaffected.
2. Text totals ≠ standard integration of the archived product: N fluxes/NPP uniformly −10.7 % (double land-fraction weighting fits to 1–3 %);
   C-cost totals (2.5/1.6 Pg C/yr) and AM/EcM split not reproducible; plotted Fig. 4a ≈ +8 %. Zonal means match.
3. Fig. 5a "symbiotic fixation" is the free-living flux (colour-bar match 1.09); symbiotic fixation ≈ 0 (Defect C).
4. C4 grass = 90 % of the global C cost of N acquisition (289 g C m⁻² yr⁻¹, 13.5 gC/gN); default parameters, normal root C — unexplained.
5. Fig. 9 classes reproduce with a ±8 % log-symmetric band on R = (leaf N:P)/(retranslocated N:P).
6. Carbon budget: [pending budget_closure.log] GPP − AR − HR − fire − LUC vs dC/dt.
7. ILAMB (2.7 data): GPP, LAI, NEE, Reco scores and ordering reproduced within ~0.04; biomass ordering reproduced (different dataset);
   NBP score destroyed by the 2009–2010 collapse unless trimmed. [scores_published_run1.csv; trimmed rerun pending]

## 2. Side-by-side (1994–2005) — filled by run_eval.sh
- headline_numbers → `numbers_1994-2005.md`; per-PFT → `pft_table_1994-2005.md`
- Fig 3/4/S10/S11 → `fig3_4_S10_S11_*.png`; Fig 5/6/7/S5 → `fig{5,6,7,S5}_1994-2005_*.png`; Fig 8 → `fig8_*.png`; Fig 9 → `fig9_*.png`
- ILAMB all five → `ilamb/scores_all_1994-2005.csv`

## 3. Still needed from the author
- ISLSCP II (IGBP) NPP and Fisher et al. (2012) TNL layers; CMIP6 11-model NPP (Arora et al. 2020 set) for Fig. 3/4b.
