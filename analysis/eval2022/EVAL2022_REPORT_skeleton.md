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

## 1b. OPEN — carbon-budget non-closure of the 2022-tree flux diagnostics (`budget_closure.py`, `budget_closure.log`)
Global 1994–2005 (archived products) and 1860–1879 (control), Pg C/yr:
| product | GPP | AR | HR | fire (PFT_FIRE_CLOSS) | GPP−AR−HR−fire−LUC | d(stocks)/dt | unexplained |
|---|---|---|---|---|---|---|---|
| archived ELM (FUN off) | 146.3 | 75.0 | 99.6 | 5.8 | −35 | +7.5 | ≈ −42 |
| archived FUN2.0 | 143.3 | 86.4 | 84.1 | ~3 | −31 | +5.8 | ≈ −37 |
| archived FUN3.0 | 122.8 | 86.6 | 51.9 | 2.9 | −19 | +2.3 | ≈ −21 |
| control rerun (FUN-P on) 1860–79 | 96.3 | 70.0 | 44.2 | 1.6 | −20 | −3.8 | ≈ −16 |
| FN spin-up, 2020 tree, FUN off | 111.0 | 69.4 | 37.9 | n/a | +3.8 (= fire) | ~0 | ≈ 0 |
The 2020 tree closes; every 2022-family product does not: HR exceeds the litter + CWD inputs (archived ELM: 99.6 vs 60.3 + 12.4)
while soil carbon rises, and the model's own NEE/NBP diagnostics (a 20–37 Pg C/yr source) follow the fluxes, not the stocks.
The internal balance check of the 2022 tree closes to ≈ 4e-5 gC/m² per hour (≈ 0.05 Pg C/yr globally) in the FUN-off test, so the
state is conserved and the inconsistency is in the history flux diagnostics (candidates: FUN cost booked into AR *and* respired as
HR after entering the soil — explains ≈ 10 of the control's 16; a double accumulation of decomposition fluxes in the 2022 tree for the
FUN-off case — unexplained 42 Pg C/yr in the archived ELM). Consequences if confirmed: the paper's ER, NEE, NBP, Fig. S10/S11 and the
ILAMB Reco/NEE/NBP scores are built on inconsistent fluxes; NPP, GPP, stocks and nutrient fluxes are not affected. Proposed test:
a short FUN-off transient in the 2022 tree with the balance report re-enabled and HR compared with the soil-C tendency.
