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
