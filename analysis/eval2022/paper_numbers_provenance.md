# Provenance of the headline numbers in Braghiere et al. (2022): which run do they come from?
Global 1994–2005 totals recomputed with area × landfrac from every surviving 1994–2005 FUN-P output in
`/home/braghiere/models_v3.2/output/global/` and from the archived product (`ELM_FUN_output/ELM_FUNP`, = v6).
Units: N and P fluxes Tg/yr; NPP and C costs Pg C/yr. "paper" = values quoted in the text/abstract.

| quantity | paper | v3_funp (Jul 2020) | v5_funp (Aug 2020) | **v6_funp = archived product** | v7_funp (Oct 2020) |
|---|---|---|---|---|---|
| mycorrhizal N uptake (NACTIVE) | 659.9 | 598.0 | 575.6 | 739.2 | 764.3 |
| AM / EcM N | 482.1 / 177.8 | 427.9 / 160.7 | 432.6 / 143.0 | 590.8 / 148.4 | 615.3 / 149.0 |
| direct-root N (NNONMYC) | 84.3 | 162.7 | 166.3 | 94.4 | 84.1 |
| N retranslocation | 97.6 | 101.8 | 104.5 | 109.2 | 109.6 |
| mycorrhizal P (PACTIVE) | 20.0 | 43.5 | 44.6 | 21.3 | 21.4 |
| direct-root P | 20.9 | 0.6 | 0.6 | 24.6 | 24.9 |
| P retranslocation | 7.3 | 0.4 | 7.5 | 7.9 | 7.9 |
| NPP | 32.2 | 32.5 | 33.8 | 36.2 | 36.5 |
| C cost of N acquisition | 2.5 | 7.5 | 7.3 | 3.77 | 3.0 |
| C cost of P acquisition | 1.6 | 7.1 | 5.2 | 4.92 | 4.5 |

Reading: no single surviving run reproduces the published set. The archived v6 product has the paper's *pathway structure*
(direct-root N ≈ 84–94, P retranslocation ≈ 7.3–7.9) but every N flux and NPP are a uniform ~11 % higher than the paper
(ratio 0.89–0.90 for NACTIVE, NNONMYC, NRETRANS, NPP; also ELM 71.5 vs 64.8 and FUN2 57.0 vs 51.2 Pg C/yr), which indicates
a systematic difference in the global area weighting used in 2020 rather than a different simulation (tested below). The
C-cost totals (2.5 and 1.6 Pg C/yr) and the AM/EcM split (73/27 vs 80/20) cannot be reproduced from any surviving file.

## Weighting test (archived products, 1994–2005 means)
| product | paper NPP | area×landfrac | area×landfrac² | area×landfrac×f_veg |
|---|---|---|---|---|
| ELM | 64.8 | 71.3 | 65.4 | 69.5 |
| ELM-FUN2.0 | 51.2 | 56.9 | 52.2 | 55.4 |
| ELM-FUN3.0 | 32.2 | 36.2 | 33.2 | 35.3 |
FUN3.0 N fluxes with area×landfrac²: NACTIVE 678 (paper 659.9), NNONMYC 86.9 (84.3), NRETRANS 100.0 (97.6), PACTIVE 19.6 (20.0),
PNONMYC 22.7 (20.9), PRETRANS 7.2 (7.3). A double land-fraction weighting reproduces the paper's N, P and NPP totals to within
1–3 %; the correct area×landfrac integration is 10–11 % higher. The paper's C-cost totals (2.5 / 1.6 Pg C/yr) and AM/EcM split
are not reproduced by any weighting of any surviving run. Fig. 9 thresholds calibrated on the archived product: R < 0.927
(N-limited) / R > 1.082 (P-limited), a log-symmetric ±8 % band, giving 6.0 / 80.1 / 13.9 % (paper 6.1 / 80.0 / 13.9 %).

## What the paper's own figures show (checked against the published images)
- Fig. 3a (zonal mean NPP, 1994–2005): the published curves (E3SM peak ≈ 1400, FUN3.0 ≈ 800 g C m⁻² yr⁻¹ at the equator) match our
  recomputation from the archived products (1410 / 780). Zonal means are independent of the global area weighting.
- Fig. 4a (global NPP 1850–2010): the published lines reach ≈ 78–80 (ELM), ≈ 60 (FUN2.0), ≈ 38–40 (FUN3.0) Pg C/yr by 2005, i.e. ≈ 8 %
  ABOVE our area × landfrac integration (71.5 / 57.0 / 36.3 for 1994–2005), whereas the text values (64.8 / 51.2 / 32.2) are ≈ 10 %
  BELOW it. The text and the figure therefore used different weightings; neither is the standard area × landfrac integration.
  The published box plots show outliers at ≈ 5–20 Pg C/yr for all three products — consistent with the 2010 CO₂ collapse being
  present in the plotted data.

## The paper's maps come from the archived v6 product, and Fig. 5a is mislabelled
Colour-bar maxima of the published Fig. 5 versus the archived product's 1994–2005 land maxima (g N m⁻² yr⁻¹):
direct root uptake 3.64 vs NNONMYC 3.644; retranslocation 3.46 vs NRETRANS 3.458; AM uptake 21.99 vs NAM 21.989 (exact matches, so
the maps were drawn from this product). Panel (a) "symbiotic biological N fixation", colour bar to 1.09, matches **FFIX_TO_SMINN**
(free-living fixation, max 1.093; Amazon 0.72, Congo 0.79), whereas symbiotic **NFIX** has a maximum of 0.001 and a global total of
0.00 Tg N/yr (Defect C: hardcoded fixation cost 900–27,000 gC/gN). Fig. 5a therefore shows free-living fixation, and the paper's
"total biological N fixation 35.3 Tg N/yr" (compared with Davies-Barnard & Friedlingstein's 52–130) is free-living fixation only.

## The archived product and the released code are different versions (settled 2026-09-19)
- The paper's public code (github.com/braghiere/E3SM-FUN3.0, `E3SMv1-FUN3.0.patch`) is byte-identical to the local v7 patch and carries the
  **23 Sep 2020** `CNFUNMod.F90` (md5 a2f2674b) — the same file as the 2022 tree used for our reruns (kn_nonmyc tiers 0.15, fixation
  override, PFT-7 typo, larch tier all present).
- The archived v6 product (Zenodo) was produced on **29 Aug 2020** with an earlier module (md5 f38e9ed0, kept in
  `models_v3.2/output/global/fix_global_v5_1994_2005/`): 72 code lines differ, all FUN cost constants — e.g. default active tier
  kc/kn 0.3/0.1 → 0.15/0.025; default non-mycorrhizal kc/kn 0.01/0.90 → 0.15/0.15; the C4-grass/17/18 non-myc tier 0.10/9.00 → 0.15/0.15.
- Consequence, visible in the side-by-side: the control (released code) reproduces the archived N and P fluxes, NPP, GPP and stocks
  within 1–3 % but not the carbon-cost diagnostics: C cost of N acquisition 3.05 vs 3.77 Pg C/yr (−19 %), mycorrhizal N-cost carbon
  2,134 vs 2,815 Tg C/yr, and a different P-cost partition (mycorrhizal 415 vs 948, root 412 vs 1,058 Tg C/yr; total 4.46 vs 4.92).
  The paper's C-cost figures (Fig. 8, S5) and text therefore describe a code state that is not the released one.
